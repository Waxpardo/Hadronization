# M2 — which quark indexes `probQQ1toQQ0join`

**Verify-before-rewrite since the review landed. Settled 2026-08-09 by reading
the pinned PYTHIA 8.317 source.** Owner decision item; **no paper edit made.**

---

## THE ANSWER

**The four-vector is indexed by the heavier of the two quarks being joined
*into the diquark* — not by the heaviest quark in the baryon.**

```
Pythia8/src/FragmentationFlavZpT.cc:523   int StringFlav::makeDiquark(int id1, int id2, int idHad)
                                  :525     int idMin = min( abs(id1), abs(id2));
                                  :526     int idMax = max( abs(id1), abs(id2));
                                  :536   } else if (idMin != idMax) {
                                  :537     if (rndmPtr->flat() > probQQ1join[min(idMax,5) - 2]) spin = 0;
```

with the vector read once at `:52-54`:

```
vector<double> pQQ1tmp = settingsPtr->pvec("StringFlav:probQQ1toQQ0join");
for (int i = 0; i < 4; ++i)
  probQQ1join[i] = 3. * pQQ1tmp[i] / (1. + 3. * pQQ1tmp[i]);
```

**Index map** (`min(idMax,5) - 2`):

| index | `idMax` | flavour |
|---|---|---|
| **0** | 2 | **u / d — light** |
| 1 | 3 | s |
| 2 | 4 | c |
| 3 | 5 (or ≥5) | b |

`idMax = 1` would give −1, but that requires `idMin == idMax == 1`, which the
`idMin != idMax` guard at `:536` excludes. **No out-of-range path.**

---

## THE REVIEW'S M2 CLAIM IS CORRECT

> *the applicable entry is identical for charm and beauty baryons with light
> diquarks*

**Confirmed.** Λ_c is `c + (ud)`; Λ_b is `b + (ud)`. In both, the **diquark is
`(ud)`**, so `idMax = 2` and **both consume index 0**. The heavy quark sits at
the *other* string end and never enters `makeDiquark`'s argument pair.

**Indices 2 and 3 are reachable only when the diquark itself contains a charm or
beauty quark** — doubly-heavy diquarks, i.e. doubly-heavy baryons. They are not
what a Λ_c/Λ_b with a light diquark uses.

---

## JUNCTION vs NON-JUNCTION — same entry rule, different quarks offered

The brief asked for this explicitly, because it is where the manuscript's claim
lives. **The answer is that they do *not* consume different entries: both call
the same `makeDiquark` with the same indexing.** What differs is *which two
quarks get joined*.

| path | call site | the two quarks joined |
|---|---|---|
| **non-junction** string break | `FragmentationSystems.cc:337` — `makeDiquark(idQA, idQB)` | the two quark ends being combined at the break |
| **junction** | `StringFragmentation.cc:2399` — `makeDiquark(idMin, idMid)` | **remnant flavours of the two lowest-momentum legs** |
| beam remnant | `BeamParticle.cc:870,1402,1890` — passes `idBeam` | valence quarks; **can** take the SU(6) branch |

**Junction leg ordering** (`StringFragmentation.cc:2112-2117`): `legMin` and
`legMax` are the smallest- and largest-momentum legs **in the junction rest
frame**; `legMid` is the remainder. The diquark is built from **`legMin` and
`legMid`**.

**And `idMin`/`idMid` are remnants, not the original leg partons**
(`:2344,:2347` — `posEnd.flavOld.id`, the flavour left at the end of fragmenting
each of those two legs). A heavy quark therefore reaches the diquark **only if it
survives as the remnant end of one of the two lower-momentum legs** — i.e. it was
not already consumed into a hadron during that leg's fragmentation.

> **So the junction topology is the one case where a heavy quark *can* land
> inside the diquark and select index 2 or 3 instead of 0.** Reading the code
> establishes that the path **exists**; it does **not** establish how often it is
> taken. **That is a measurement, not a code question, and this note does not
> assert a rate.**

**One further branch, for completeness:** `:532-534` — if `idHad` is a proton or
neutron and the pair is `(ud)`, spin is 0 with probability 0.75 by SU(6),
**bypassing `probQQ1join` entirely**. The junction call passes `idHad = 0`
(default), so junction fragmentation never takes this branch; the beam-remnant
calls do pass a beam id and can.

---

## WHAT IT MEANS FOR `Results.tex`

**The paragraph's premise survives**: for charm and beauty baryons formed with a
**light diquark**, `probQQ1toQQ0join` supplies the **same** entry — index 0 — so
a tune change to that entry moves charm and beauty baryons **together**, and the
entry cannot by itself produce a charm-versus-beauty asymmetry in that channel.

**The qualification the text should carry** is the junction case: the parameter
is per-diquark-flavour, and junction fragmentation can form a diquark from
remnant ends that include a heavy quark, which would select a different entry.
Whether that matters numerically is unmeasured here.

**Owner decision. No edit made to `Paper/**`.** If the paragraph currently says
"identical entry" without qualification, it is correct for the light-diquark case
it describes and incomplete only if it is read as covering junction topologies
too.

---

## Provenance

- Source: `/data/alice/ipardoza/pythia_stock_8317/pythia8317/src/`, the **pinned
  8.317 install** the producer links against — not a distribution copy.
- `probQQ1toQQ0join` appears in exactly three places in
  `FragmentationFlavZpT.cc`: read at `:52`, transformed at `:54`, consumed at
  `:537`. The scalar `probQQ1toQQ0` (no `join`) is a different parameter with its
  own uses at `:49,144-147,167-174,512,556,588-596` and is **not** what this note
  is about.
