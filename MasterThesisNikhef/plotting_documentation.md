# configuration.json documentation

Introduction
---
The macro is executed by running `root 'improvedPlotting.C("configuration.json")'` with your favourite configuration file. This configuration file takes several settings necessary for the calculation of the yields and the drawing. It is (mostly) very general and can be extended easily, allowing for freedom and it prevents having to delve deep into the code to find certain parameters. 
TODO: add github link
&nbsp;&nbsp;&nbsp;&nbsp; Below you can find a short summary of all the parameters that can be set and what type they expect. Some comments are given as well, when relevant.

Error subsampling
-
- `"VERBOSE"`: bool
Option to print much more output. Can be added in code if more checks are necessary.
- `"calculate_errors"`: bool
Turn on ("true") when subsampling needs to be applied to calculate the errors. Can only be used if the subsample directories exist and are in the predicted format (see example[link] on github). When off ("false") the error is set at a non-sensical 1e-10, as it is necessary to asign an error for the drawing.
- `"bb_bar_complete_root_dir_sub_samples"`: string
The path to the `combined_root_subSamples_bb_250` directory. Expects the `_{TUNE}` suffix, but is not added in the configurations here, in order to be flexible in using tunes.
- `"cc_bar_complete_root_dir_sub_samples"`: string
Same as above, but for the charm case
- `"nSubSamples"`: int
Number of sub samples to be used. Cannot exceed the number of files in the sub_samples directory.

Path configurations
-
- `"base_dir"`: string
Path to directory with the root files (default: RootFiles) 
- `"PYTHIA_TUNES"`: [
&nbsp;&nbsp;&nbsp;&nbsp; string1,
&nbsp;&nbsp;&nbsp;&nbsp; string2,
&nbsp;&nbsp;&nbsp;&nbsp; ...
  ]
As many tunes can be added as desired. The names have to coincide with the `_{TUNES}` suffices given in the input directories.
- `"bb_bar_complete_root_dir"`: string
Path to beauty simulation outputs. Expects all trigger-associate correlations for both opposite-sign and same-sign pairs. The directory itself should have the `_{TUNE}` suffix, but it should not be given in the path here. The code adds this automatically.
- `"cc_bar_complete_root_dir"`: string
Path to the charm simulation outputs. Equivalent to beauty case.

NOTE: it should be straightforward to add other flavours (or prompt/non-prompt) pairs here. Different simulation settings should be put in the `PYTHIA_TUNES` argument, however.

Trigger-associate correlations
-
The opposite-sign (OS) and same-sign (SS) pairs are given here. The cases for beauty and charm (and possibly other flavours) are identical.
Each entry contains a few parameters that describe the trigger and associate names (for OS and SS) as well as the file name where they can be found.

{

-  `"trigger"`: string
e.g. "Bˆ{+}",
-  `"associateOS"`: string
e.g. "B-",
-  `"associateSS"`: string
e.g. "Bˆ{+}",
-  `"OS"`: string
e.g. "BplusBminus.root",
-  `"SS"`: string
e.g. "BplusBplus.root"

}

Currently still investigating a bug where the latex formatting is not respected on the x-axis (which is why the `associateOS` name is not in latex.)

Dependencies
-
Each entry has the exact name of the histogram that contains the dependency (e.g. low-low for pT, mult40_80 for multiplicity or FF for rapidity) and the exact name of the appropriate trigger spectrum (which is used to normalise the total number of pairs). The names appearing in the legend are set later on.

{

- `"hDPhi"`: string
e.g. "hDPhiLL"
- `"hTrPt"`: string
e.g. "hTrPtL"

}

NOTE: if the simulation and analysis procedure switches to a `THnSparse` and user range approach, this input structure has to be modified (alternatively, for backwards compatibility, another part could be added and a bool can be set to pick one or the other).

Plotting - setting the canvases
-
This is where the fun things happen. The user can define an unlimited amount of canvases and select from a broad range of settings to create plots, without diving deep into the code. Many options are not required and can be left empty (-1 or "NONE"). If one wants to combine many plots on a larger, global canvas, you also have to define these 'mini' canvases seperately. This gives a lot of freedom in how things are set, though it overcrowds the file quite quickly. Sometimes it might be better to create a new `configuration.json` file for other plots.

The essence of the plotting is done with the `"draw_function_to_use"` setting, which selects the function as defined in the macro to make the desired plot. This gives in prinicipal ultimate freedom to define new plots (even with hard-coded settings, if desired).

Each entry has the following structure:
{

-  `"canvas_name"`: string
Internal canvas name, not displayed. Name is used to find canvases to plot on global canvas (exact match required; in the example configurations they always start with `mini_`).
-  `"draw_function_to_use"`:
Exact match to function name used to draw. The four standard ones allow to draw the balancing yields and the baryon/meson ratio yields. In addition, one can draw the ratio between two specified tunes of these two quantitites.
-  `"TUNES"`: [
&nbsp;&nbsp;&nbsp;&nbsp; string1,
&nbsp;&nbsp;&nbsp;&nbsp; string2,
&nbsp;&nbsp;&nbsp;&nbsp; ...
  ]
The tunes that will be used to draw. They need to have an exact match with at least one of the tunes given earlier (in the `"PYTHIA_TUNES"` argument above).
-  `"FLAVOUR"`: string
The flavour that will be used to draw the plots (`BEAUTY` or `CHARM`). Currently there is no possiblity to draw beauty and charm entries on the same pad, as it is not used. This could be implemented by adding more drawing functions and specifying them in the `"draw_function_to_use"` argument.
-  `"nominator_TUNE"`: string
Name of tune to be used in `TUNE_{nominator} / TUNE_{denominator}` comparisons. Can be done for both the 'normal' yields and the baryon/meson ratio yields. Needs to be an exact match with one of the tunes above and is a necessary argument if the tune ratio plotting is given in the `"drawing_functions_to_use"` argument above.
-  `"denominator_TUNE"`: string
Denominator tune name of tune ratios
-  `"baryons_to_plot_in_baryon/meson_ratio"`: [
&nbsp;&nbsp;&nbsp;&nbsp; string1,
&nbsp;&nbsp;&nbsp;&nbsp; string2,
&nbsp;&nbsp;&nbsp;&nbsp; ...
  ]
List of baryons to plot in the baryon/meson ratio plots (if enabled). Need to be exact matches to baryons as given in the `"associatesOS"` argument.
- `"use_hard_coded_settings"`: bool
'Corner of shame'. Sometimes (in particular for legend entries) it's easier or necessary to propagate specific settings to the canvas which cannot be realised with the existing options. In this case one sets this option to `true` and adds in the source code a small block that does exactly what one wants. It is not sufficient to set this parameter to `true`, you should also use the `isCanvasNameEqualTo()` function that returns a bool depending on if the current canvas name is equal to the demanded one (`canvas_name`). This way the user can take a specific canvas out and only apply the hard-coded options there. This option exists so that anyone copying the `configuration.json` doesn't strangely start drawing some weird things they didn't ask for.
-  `"write"`: bool
Save output yes or no (standard as .PDF, .C, .PNG)
-  `"write_path"`: string
Path to write outputs to
-  `"write_name"`: string
Name to use to write output canvas.
-  `"canvas_title"`: string
Name of canvas title, will be displayed on top of canvas.
-  `"x_axis_title"`: string
X-axis title
-  `"y_axis_title"`: string
Y-axis title
-  `"x_size_canvas"`: double
First size argument of TCanvas()
-  `"y_size_canvas"`: double
Second size argument of TCanvas()
-  `"x_min_mini_pad"`: double
If all of the mini_pad settings are given and unequal to -1, then the canvas will also be drawn on a mini pad, which can be propagated to the global canvas. In addition, the margins for these pads can also be set here.
-  `"x_max_mini_pad"`: double
-  `"y_min_mini_pad"`: double
-  `"y_max_mini_pad"`: double
-  `"top_margin_mini_pad"`: double
The margins can be used when pads are overlapping each other or title disappear, etc.
-  `"bottom_margin_mini_pad"`: double
-  `"left_margin_mini_pad"`: double
-  `"right_margin_mini_pad"`: double
-  `"y_min_axis"`: double
Maximum value of y-axis
-  `"y_max_axis"`: double
Minimum value of y-axis
-  `"histogram_minimum"`: double
Similar to above - but can be set slightly higher than y-axis range to avoid overlap between two pad y-axis labels or ticks.
-  `"histogram_maximum"`: double
Same as `"histogram_minimum"` but for the maximum value.
-  `"set_log_y"`: bool
Option to set a logarithmic scale on the y-axis.
-  `"x_min_legend"`: double
If all of the legend values are given and nonequal to -1, the legend will be drawn in a box with positions x1(x_min_legend,y_min_legend) and x2(x_max_legend,y_max_legend).
-  `"x_max_legend"`: double
-  `"y_min_legend":` double
-  `"y_max_legend"`: double
-  `"legend_entries"`: [
    {
&nbsp;&nbsp;&nbsp;&nbsp; `"object_name"`: string
Exact name of dependency object (is not used for baryon/meson ratios). TODO: probably better to add this to the configuration part where the dependenies are given. Possibly also do that for the baryons then.
&nbsp;&nbsp;&nbsp;&nbsp; `"display_name"`: string
Name which is shown in the legend
    },
    {
&nbsp;&nbsp;&nbsp;&nbsp;...
    }
  ]
-  `"TUNE_colours"`: [
NOTE: this can be left empty for the tune ratio plots (it is not used there).
    {
&nbsp;&nbsp;&nbsp;&nbsp; `"TUNE_name"`: string
The name of the tune and the colour in which it should be drawn. Also this section should be moved to another category.
&nbsp;&nbsp;&nbsp;&nbsp; `"colour"`: int
Colour is given with `int` and translated to `kColor`.
    },
    {
&nbsp;&nbsp;&nbsp;&nbsp; ...
    }
  ]
-  `"dependency_line_styles"`: [
    {
&nbsp;&nbsp;&nbsp;&nbsp; `"dependency_name"`: string
Exact name of dependency object (as given in dependencies above)
&nbsp;&nbsp;&nbsp;&nbsp; `"line_style"`: int
Line style is given with `int` and translated to `kLineStyle`. Not used in baryon/meson ratio plots.
    },
    {
&nbsp;&nbsp;&nbsp;&nbsp; ...
    }
  ]
-  `"baryon_line_styles"`: [
    {
&nbsp;&nbsp;&nbsp;&nbsp; `"baryon_name"`: string
Name of baryon (has to be one of the baryons to be plotted in this baryon/meson ratio plot).
&nbsp;&nbsp;&nbsp;&nbsp; `"line_style"`: int
Line style is given with `int` and translated to `kLineStyle`. Only used in baryon/meson ratio plots.
    },
    {
&nbsp;&nbsp;&nbsp;&nbsp; ...
    }
  ]

}

Plotting - creating a global canvas
-
It is meaningful to combine several smaller results and tune ratio 'mini pads' into a larger, 'global' canvas. This way the results can be compared more straightforwardly and certain information does not have to be given redundantly (e.g. legend entries, x-axis, etc.). The global canvas entries contain some generic settings which were already used above (canvas name, write name, canvas sizes) and a list of the mini pads to be used (using the exact names as given in the canvas settings list above). Each global canvas entry then takes this form:

TODO: fix the weird code black box thing?
{

-   `"canvas_name"`: string
-   `"canvas_title"`: string
-   `"mini_canvases"`: [
    string,
    string,
    ...
  ]
List of mini canvas names as given in the canvas configuration settings above (in the `canvas_name` argument). All canvas-specific settings are also given in the canvas configuration settings and not in this entry.
-   `"write"`: bool
-   `"write_path"`: string
-   `"write_name"`: string
-   `"x_size_canvas"`: double
-   `"y_size_canvas"`: double 

}

Overview of standard `configuration.json` files in directory
-
NOTE: the standard lay-out logic is the same in all of the files. The files follow the same structure as used in the documentation here. The canvas settings are given with the following logic in mind:
- First standalone canvases
- Within the standalone canvases, first the beauty cases, then charm.
- Within the flavour cases, first the integrated yield plots, followed by the tune ratio plots (usually only junctions/monash). Afterwards the baryon/meson ratio and their tune ratios ('ratio of ratio plots').
- After the standalone canvases, the mini canvases. They follow mostly the same order as before, but the mini pads that will be combined on the same global canvas stay together (i.e. beauty and charm will alternate each other).

The following standard configuration files can be found in the repo:
- TODO







