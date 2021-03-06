"""
Plots all Nanocompare paper out
"""
import os
import sys
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import matplotlib.patches as mpatches

import matplotlib.colors as mcolors

import pandas as pd
import seaborn as sns
from scipy.stats import pearsonr

from nanocompare.meth_stats.count_m_c_sites import load_count_ds_original
from nanocompare.global_settings import tools, locations_category, locations_singleton, tools_abbr, map_from_tool_to_abbr, nanocompare_basedir, agressiveHot, cor_tsv_fields, perf_order, dict_cor_tsv_to_abbr, cor_tsv_fields_abbr
from nanocompare.collect_data import collect_box_plot_all_data
from nanocompare.load_data import load_running_time_and_mem_usage, get_one_dsname_perf_data, get_performance_from_datasets_and_locations, load_box_plot_all_data, load_corr_data_tsv_fns, load_all_perf_data, load_all_perf_data_for_dataset, load_all_perf_data_for_dataset_list, load_sing_nonsing_count_df
import numpy as np

tcgajax_prj = "/projects/li-lab/nmf_epihet/tcgajax"
sys.path.append(tcgajax_prj)

from lilab.tcga.global_tcga import *
from lilab.tcga.utils import current_time_str
import nanocompare.legacy.performance_plots as pp
from lilab.tcga.rutils import smooth_scatter_call_r

from lilab.tcga.picture import scatter_plot_x_y_smoothlike


def single_ds_5mc_5c_performance(dsname="HL60_AML_Bsseq_cut5"):
    df_sel = get_one_dsname_perf_data(dsname)

    style = 'Location'
    filled_markers = ('o', 'P', '>', 's', 'X')
    filled_markers = ['o', 'P', '>', 's', 'X']

    ax = sns.scatterplot(x="Location", y="Performance", hue='Tool', data=df_sel, style=style, markers=filled_markers, s=100, alpha=0.85, linewidths=None)

    # ax = sns.stripplot(x="Location", y="Performance", hue='Tool', size=8, data=df_sel)

    # sns.catplot(x="time", y="pulse", hue="kind", data=exercise)

    # ax = sns.catplot(x="Location", y="Performance", hue='Tool', data=df_sel)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    # Put a legend to the right of the current axis
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    outfn = os.path.join(pic_base_dir, f"singleds_nanocompare_location_f1_5c_5mc_performance_time_{current_time_str()}.png")
    ax.figure.savefig(outfn, format='png', dpi=600)
    logger.info(f"save to {outfn}")
    plt.show()


def set_style(font_scale=1.2):
    # sns.set()
    # sns.set(font_scale=1.15)
    # sns.set_style("white")

    # This sets reasonable defaults for font size for
    # a figure that will go in a paper
    sns.set_context("paper")
    sns.set(font_scale=font_scale)

    # Set the font to be serif, rather than sans
    # sns.set(font='serif')

    # Make the background white, and specify the
    # specific font family
    # sns.set_style("white", {
    #         "font.family": "serif",
    #         "font.serif" : ["Times", "Palatino", "serif"]
    #         })
    sns.set_style("white")


def cut_abbr_dsname(dsname):
    """
    Cut the abbr from dsname with other useful info
    :param dsname:
    :return:
    """
    return dsname[0:dsname.find('_')]


def set_labels_fig_3a(grid, ds_list, location_list, meas_list=['F1_5mC', 'F1_5C']):
    """
    Set labels of figure 3A, FacetGrid
    :param grid:
    :return:
    """

    nrow = len(perf_order)
    ncol = len(ds_list)
    [plt.setp(ax.texts, text="") for ax in grid.axes.flat]
    # grid.set_titles(row_template='{row_name}', col_template='{col_name}')
    # grid.set_xticklabels(rotation=45)

    grid.set_titles(row_template='', col_template='')
    # grid.set_xticklabels([])
    # grid.set(xticks=[])

    # Iterate through each axis
    for axi, ax in enumerate(grid.axes.flat):

        # only set first col figure's Y axis label
        if axi % ncol == 0:
            ax.set_ylabel(meas_list[axi // ncol])
        else:
            ax.set_ylabel("")

        if axi < ncol:
            ax.set_title(cut_abbr_dsname(ds_list[axi]))

        ax.set_xticklabels([])

    grid.fig.tight_layout()

    legend_format = {'Sex (hue)': ['Male', 'Female'],
            'Group Size (size)' : ['0', '2', '4', '6'],
            'Smoker (shape)'    : ['Yes', 'No']
            }

    legend_data = grid._legend_data

    # modify legend label to another one
    # legend_data["Tool"] = legend_data.pop("Tool")

    # keep this label order to print dict of legend_data
    # label_order = ['Tool'] + tools_abbr + ['Location'] + location_list

    grid.add_legend(label_order=legend_data)
    # plt.legend(loc='upper left', bbox_to_anchor=(1, 0.5))
    pass


def scatter_facet_grid_multiple_ds_5mc_5c_performance(ds_list=['K562_WGBS_joined', 'APL_BSseq_cut10', 'HL60_AML_Bsseq_cut5'], location_list=locations_category, meas_list=['F1_5mC', 'F1_5C']):
    """
    Generate three datasets 5mc and 5C results in a FacetGrid
    :return:
    """
    df = get_performance_from_datasets_and_locations(ds_list=ds_list, location_list=location_list, meas_list=meas_list)

    df['Location'] = df['Location'].replace({"GW": "Genome-wide", 'singletons': 'Singletons', 'nonsingletons': 'Non-singletons', 'discordant': 'Discordant', 'concordant': 'Concordant', 'cpgIslandExt': 'CpG Island', 'exonFeature': 'Exons', 'intergenic': 'Intergenic', 'promoters_500bp': 'Promoters', 'intronFeature': 'Introns'})

    # Set the style for plotting
    set_style(font_scale=1.5)

    # style = 'Location'

    # figure specific settings
    filled_markers = ('o', 'P', '>', 's', 'X', '^')
    marker_size = 120

    perf_order = meas_list

    grid = sns.FacetGrid(df, row='Measurement', col='Dataset', row_order=perf_order, margin_titles=True)

    # grid.map_dataframe(sns.catplot, x="Location", y="Performance", hue='Tool', hue_order=tools_abbr)

    grid.map_dataframe(sns.scatterplot, x="Location", y="Performance", hue='Tool', style="Location", markers=filled_markers, hue_order=tools_abbr, s=marker_size, x_jitter=3, y_jitter=5)

    # Set plot labels
    set_labels_fig_3a(grid, ds_list=ds_list, location_list=location_list, meas_list=meas_list)

    # Save plot and show if possible
    outfn = os.path.join(pic_base_dir, f"scatter_facet_grid_multiple_ds_location_{location_list[0]}_f1_{meas_list[0]}_performance_time_{current_time_str()}.png")
    grid.savefig(outfn, format='png', bbox_inches='tight', dpi=600)
    logger.info(f"save to {outfn}")
    plt.show()


# Not finished yet
def box_plots_all_locations1():
    prefix = current_time_str()
    metrics = ["F1_5C", "F1_5mC"]

    df = load_box_plot_all_data()

    sel_cols = ['Tool', 'BasecallTool', 'Location', 'F1_5C', 'F1_5mC']
    df1 = df[sel_cols]
    df1 = df1.rename(columns={'Tool': 'Dataset', 'BasecallTool': 'Tool'})

    refinedf = pd.melt(df1, id_vars=['Dataset', 'Location', 'Tool'], var_name='Measurement', value_name='Performance')

    logger.debug(f"refinedf={refinedf}")

    regions0 = ["singletons", "nonsingletons", "discordant", "concordant"]
    regions1 = ["GW", "cpgIslandExt", "promoterFeature", "exonFeature", "intronFeature", "intergenic"]
    regions_list = [regions0, regions1]

    for r, region in enumerate(regions_list):
        df2 = refinedf[refinedf['Location'].isin(region)]

        # with sns.plotting_context(font_scale=3):
        sns.set(font_scale=2)
        sns.set_style("white")

        # sns.set(style="ticks")

        # palette = sns.color_palette(['blue', 'orange', 'green', 'red'])

        # hue="Tool", hue_order=tool_list,, palette=palette

        row_order = ['F1_5C', 'F1_5mC']
        col_order = region
        plt.figure(figsize=(25, 10))
        plt.rcParams.update({'font.size': 15})

        # violin  box
        grid = sns.catplot(data=df2, row='Measurement', col="Location", x="Tool", y="Performance", hue="Tool", order=tools, hue_order=tools, kind="violin", height=4, aspect=0.8, row_order=row_order, col_order=col_order, width=0.8)

        # ax = sns.boxplot(x="Tool", y="Performance", data=df2)

        outfn = os.path.join(pic_base_dir, f"box_plot_region{r}_{current_time_str()}.png")

        ncol = len(col_order)
        for ti, ax in enumerate(grid.axes.flat):
            col_index = ti % ncol
            if ti // ncol == 0:
                ax.set_title(col_order[col_index])
            else:
                ax.set_title("")
            ax.set_xticklabels([])  # , rotation=30
            ax.set_xlabel("")
            if ti == 0:
                ax.set_ylabel(row_order[0])
            elif ti == ncol:
                ax.set_ylabel(row_order[1])

            t = ti

        # [plt.setp(ax.texts, text="") for ax in grid.axes.flat]
        # plt.setp(grid.fig.texts, text="")

        # grid.add_legend()

        outfn = os.path.join(pic_base_dir, f"box_plots_allds_data_location_f1_5c_5mc_performance__region{r}_time_{current_time_str()}.png")
        grid.savefig(outfn, format='png', dpi=600)
        logger.info(f"save to {outfn}")

        plt.show()
        # break

        pass


def get_pal_4():
    set_style()
    current_palette = sns.color_palette()
    pal_plot = [mpatches.Patch(color=current_palette[i], label=tools_abbr[i]) for i in range(4)]
    return pal_plot


def box_plots_all_locations(metrics=["F1_5mC", "F1_5C"]):
    """
    # metric = "roc_auc"
    # metric = "accuracy"
    # metrics = ["accuracy", "roc_auc", "F1_5C", "F1_5mC"]

    :param metrics:
    :return:
    """

    # df = load_box_plot_all_data()
    # logger.debug(f"df = {df}")

    df = load_all_perf_data_for_dataset_list()
    logger.debug(f"df = {df}")

    folder = "reports_dump"
    prefix = current_time_str()

    # data = pp.load_data(f"{nanocompare_basedir}/reports/{folder}")
    # data = find_box_plot_data()

    # order_list = ["Tombo_calls", "Nanopolish_calls", "DeepSignal_calls", "DeepMod_calls"]
    # order_list = ["Nanopolish_calls", "DeepSignal_calls", "DeepMod_calls", "Tombo_calls"]
    # order_list = tools
    # order_list = tools_abbr

    # sns.set()
    # plt.rcParams.update({'font.size': 15})
    # sns.set(font_scale=2)
    # sns.set_style("white")

    set_style(font_scale=1.8)
    current_palette = sns.color_palette()

    # p1 = mpatches.Patch(color=current_palette[0], label=order_list[0])
    # p2 = mpatches.Patch(color=current_palette[1], label=order_list[1])
    # p3 = mpatches.Patch(color=current_palette[2], label=order_list[2])
    # p4 = mpatches.Patch(color=current_palette[3], label=order_list[3])
    # pal_plot = [p1, p2, p3, p4]

    pal_plot = [mpatches.Patch(color=current_palette[i], label=tools_abbr[i]) for i in range(4)]

    # regions = ["GW", "singletons", "nonsingletons", "discordant", "concordant", "cpgIslandExt", "cpgShoresExt", "cpgShelvesExt", "promoterFeature", "exonFeature", "intronFeature", "geneFeature", "intergenic"]
    # regions = ["GW", "singletons", "nonsingletons", "discordant", "concordant", "cpgIslandExt", "promoterFeature", "exonFeature", "intronFeature", "intergenic"]

    regions0 = ["singletons", "nonsingletons", "discordant", "concordant"]
    regions1 = ["GW", "cpgIslandExt", "exonFeature", "intergenic", 'intronFeature', "promoters_500bp"]  # ,
    regions_list = [regions0, regions1]

    # For each metric in metrics, box plot region type 0 and 1
    for metric in metrics:  # for each metric
        for r, regions in enumerate(regions_list):  # for each regine 1 category or 2 singleton
            plt.clf()
            fig = plt.gcf()
            fig.set_size_inches(20, 5)

            for i, region in enumerate(regions):
                order = i + 1
                df_filtered = df[df.Location == region]
                df_filtered = df_filtered[df_filtered[metric] > 0]
                df_filtered.head()

                logger.info(f"df_filtered={df_filtered}")

                plt.subplot(1, len(regions), order)

                # # sns.boxplot(x="method", y="AUC", hue="BinaryLabels", data=df, palette="Set1")
                # ax = sns.violinplot(x="BasecallTool", y="accuracy", data=df_filtered, palette="Set1", order=["Tombo_calls", "Nanopolish_calls", "DeepSignal_calls", "DeepMod_calls"], width=0.3)

                # x="BasecallTool",
                ax = sns.boxplot(x="Tool", y=metric, data=df_filtered, order=tools_abbr, width=0.65, palette=sns.color_palette())

                if i == len(regions) - 1:
                    # hue="BasecallTool",
                    # fig.legend(handles=pal_plot, bbox_to_anchor=(0.5, 1.2), title='Tool', ncol=5)
                    plt.legend(handles=pal_plot, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., title='Tool')
                    # plt.legend(handles=pal_plot, bbox_to_anchor=(0.1, 1.2),   title='Tool', ncol=5)

                # ax = sns.stripplot(x="Tool", y=metric, data=df_filtered, order=tools_abbr, size=2.5, color=".2", edgecolor="gray", jitter=True)  # , color="grey"

                ax.set_xticklabels([], rotation=90)

                # xticks = ax.get_xticklabels()
                # xticks = 'change'
                #
                # labels = [item.get_text() for item in ax.get_xticklabels()]
                # labels[0] = 'Testing'

                # ax.set_xticklabels(labels, rotation=45)

                # plt.setp(ax.get_xticklabels(), rotation=45)

                # a = ax.get_xticks().tolist()
                # a[0] = 'change'
                # # ax.set_xticklabels(['', '', '', ''], rotation=90)
                # plt.xticks([1, 2, 3, 4])
                #
                # # for ticki, tick in enumerate(ax.get_xticklabels()):
                # #     # tool_abbr_list[ticki]
                # #     tick.set(rotation=90)
                # #     tick.set()

                ax.set_xlabel("")

                # plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

                plt.ylim(0, 1)

                if metric == 'roc_auc':
                    ylabel_text = "AUC"
                elif metric == 'accuracy':
                    ylabel_text = "Accuracy"
                else:
                    ylabel_text = metric

                if order > 1:
                    ax.set_yticklabels([])
                    plt.ylabel("")
                else:
                    plt.ylabel(ylabel_text)

                if region == "cpgIslandExt":
                    plt.title("CpG Island")
                elif region == "promoters_500bp":
                    plt.title("Promoters")
                elif region == "intronFeature":
                    plt.title("Introns")
                elif region == "exonFeature":
                    plt.title("Exons")
                elif region == "singletons":
                    plt.title("Singletons")
                elif region == "nonsingletons":
                    plt.title("Non-singletons")
                elif region == "discordant":
                    plt.title("Discordant")
                elif region == "concordant":
                    plt.title("Concordant")
                elif region == "intergenic":
                    plt.title("Intergenic")
                elif region == "GW":
                    plt.title("Genome-wide")
                else:
                    plt.title(region)

            outfn = os.path.join(pic_base_dir, f"box_plot.metric_{metric}.region.{regions[0]}_time_{prefix}.png")

            # TODO do not show , or can not save
            # plt.show()
            # plt.savefig(outfn, format="png", bbox_inches='tight', dpi=600)
            # , bbox_extra_artists=(lgd,), bbox_inches='tight'
            plt.savefig(outfn, format="png", bbox_inches='tight', dpi=600)
            logger.info(f"save to {outfn}")

            plt.show()
        #     break
        # break

    # outfn = os.path.join(pic_base_dir, "{}.joinedReports.tsv".format(prefix))
    # data.to_csv(outfn, sep='\t', index=False)


def cor_plot():
    # files = ["Methylation_correlation_plotting_data.APL_oxBS_cut10.tsv", "Methylation_correlation_plotting_data.APL_WGBS_cut10.tsv", "Methylation_correlation_plotting_data.HL60_RRBS_rep_ENCFF000MDA_Bismark.tsv", "Methylation_correlation_plotting_data.HL60_RRBS_rep_ENCFF000MDF_Bismark.tsv",
    #         "Methylation_correlation_plotting_data.K562_WGBS_rep_ENCFF721JMB.tsv",
    #         "Methylation_correlation_plotting_data.K562_WGBS_rep_ENCFF867JRG.tsv"]
    # cor_tsv_fields = ["DeepSignal_freq", "Tombo_freq", "Nanopolish_freq", "DeepMod_freq", "DeepMod_clust_freq", "BSseq"]

    # fields = ["DeepSignal_freq", "Tombo_freq", "Nanopolish_freq", "DeepMod_freq",  "BSseq"]

    optionalSuffix = current_time_str()

    for infn in load_corr_data_tsv_fns():
        df = pd.read_csv(infn, sep='\t')
        df = df.rename(columns=dict_cor_tsv_to_abbr())

        basename = os.path.basename(infn)
        outfileName = "{}_time_{}.png".format(basename.replace(".tsv", ""), optionalSuffix)
        outfn = os.path.join(pic_base_dir, outfileName)
        position = 1

        plt.clf()

        fig, ax = plt.subplots()
        fig.set_size_inches(10, 10)

        left, width = .25, .5
        bottom, height = .25, .5
        right = left + width
        top = bottom + height

        gridRes = 30

        for y in range(1, len(cor_tsv_fields) + 1):
            for x in range(1, len(cor_tsv_fields) + 1):
                if x == y:
                    # Diagonal:
                    plt.subplot(len(cor_tsv_fields), len(cor_tsv_fields), position)
                    #             df[fields[x-1]].hist(bins=100)
                    ax = sns.kdeplot(df[cor_tsv_fields_abbr[x - 1]], shade=True, color="black")

                    ax.set_yticklabels([])
                    ax.set_xticklabels([])

                elif x > y:
                    # upper triangle:
                    ax2 = plt.subplot(len(cor_tsv_fields), len(cor_tsv_fields), position)

                    corrValue = pearsonr(df[cor_tsv_fields_abbr[x - 1]], df[cor_tsv_fields_abbr[y - 1]])
                    corrValueStr = "{0:2.2f}".format(corrValue[0])

                    ax2.text(0.5 * (left + right), 0.5 * (bottom + top), corrValueStr,
                             horizontalalignment='center',
                             verticalalignment='center',
                             fontsize=25, color='black',
                             transform=ax2.transAxes)

                    ax2.set_yticklabels([])
                    ax2.set_xticklabels([])

                elif x < y:
                    # lower triangle:
                    ax3 = plt.subplot(len(cor_tsv_fields), len(cor_tsv_fields), position)

                    plt.hexbin(df[cor_tsv_fields_abbr[x - 1]], df[cor_tsv_fields_abbr[y - 1]], gridsize=(gridRes, gridRes), cmap=agressiveHot)  # plt.cm.gray_r )

                    ax3.set_yticklabels([])
                    ax3.set_xticklabels([])

                position += 1

        fig.savefig(outfn, dpi=600, bbox_inches='tight')
        plt.show()
        logger.info(f"save to {outfn}")
        # break


def smooth_scatter_cor_plot():
    # files = ["Methylation_correlation_plotting_data.APL_oxBS_cut10.tsv", "Methylation_correlation_plotting_data.APL_WGBS_cut10.tsv", "Methylation_correlation_plotting_data.HL60_RRBS_rep_ENCFF000MDA_Bismark.tsv", "Methylation_correlation_plotting_data.HL60_RRBS_rep_ENCFF000MDF_Bismark.tsv",
    #         "Methylation_correlation_plotting_data.K562_WGBS_rep_ENCFF721JMB.tsv",
    #         "Methylation_correlation_plotting_data.K562_WGBS_rep_ENCFF867JRG.tsv"]
    # cor_tsv_fields = ["DeepSignal_freq", "Tombo_freq", "Nanopolish_freq", "DeepMod_freq", "DeepMod_clust_freq", "BSseq"]

    # fields = ["DeepSignal_freq", "Tombo_freq", "Nanopolish_freq", "DeepMod_freq",  "BSseq"]

    optionalSuffix = current_time_str()

    for infn in load_corr_data_tsv_fns():
        df = pd.read_csv(infn, sep='\t')
        df = df.rename(columns=dict_cor_tsv_to_abbr())

        basename = os.path.basename(infn)
        outfileName = "{}_time_{}.png".format(basename.replace(".tsv", ""), optionalSuffix)
        outfn = os.path.join(pic_base_dir, outfileName)
        position = 1

        logger.debug(f"df={df}")
        df.info()

        xdata = df['BSseq']
        ydata = df['DeepSignal']

        ydata = df['Tombo']

        # smooth_scatter_call_r(x=xdata, y=ydata, x_label='BGTruth', y_label=f"DeepSignal", outdir=pic_base_dir, is_show=True)

        scatter_plot_x_y_smoothlike(xdata=xdata, ydata=ydata)

        break

        plt.clf()

        fig, ax = plt.subplots()
        fig.set_size_inches(10, 10)

        left, width = .25, .5
        bottom, height = .25, .5
        right = left + width
        top = bottom + height

        gridRes = 30

        for y in range(1, len(cor_tsv_fields) + 1):
            for x in range(1, len(cor_tsv_fields) + 1):
                if x == y:
                    # Diagonal:
                    plt.subplot(len(cor_tsv_fields), len(cor_tsv_fields), position)
                    #             df[fields[x-1]].hist(bins=100)
                    ax = sns.kdeplot(df[cor_tsv_fields_abbr[x - 1]], shade=True, color="black")

                    ax.set_yticklabels([])
                    ax.set_xticklabels([])

                elif x > y:
                    # upper triangle:
                    ax2 = plt.subplot(len(cor_tsv_fields), len(cor_tsv_fields), position)

                    corrValue = pearsonr(df[cor_tsv_fields_abbr[x - 1]], df[cor_tsv_fields_abbr[y - 1]])
                    corrValueStr = "{0:2.2f}".format(corrValue[0])

                    ax2.text(0.5 * (left + right), 0.5 * (bottom + top), corrValueStr,
                             horizontalalignment='center',
                             verticalalignment='center',
                             fontsize=25, color='black',
                             transform=ax2.transAxes)

                    ax2.set_yticklabels([])
                    ax2.set_xticklabels([])

                elif x < y:
                    # lower triangle:
                    ax3 = plt.subplot(len(cor_tsv_fields), len(cor_tsv_fields), position)

                    plt.hexbin(df[cor_tsv_fields_abbr[x - 1]], df[cor_tsv_fields_abbr[y - 1]], gridsize=(gridRes, gridRes), cmap=agressiveHot)  # plt.cm.gray_r )

                    ax3.set_yticklabels([])
                    ax3.set_xticklabels([])

                position += 1

        fig.savefig(outfn, dpi=600, bbox_inches='tight')
        plt.show()
        logger.info(f"save to {outfn}")
        # break


def get_simple_title_from_ds(str):
    return str[0:str.find('_')]
    pass


def cor_box_plot():
    """
    Box plot the correlation of all or mixed CpGs
    :return:
    """

    folders = ["AML_Bsseq_cut10", "AML_Bsseq_cut5", "AML_oxBSseq_cut10", "AML_oxBSseq_cut5", "APL_BSseq_cut10", "APL_BSseq_cut5", "APL_oxBSseq_cut10", "APL_oxBSseq_cut5", "HL60_AML_Bsseq_cut5", "HL60_AML_oxBsseq_cut5", "HL60_RRBS_rep_ENCFF000MDA_Bismark", "HL60_RRBS_rep_ENCFF000MDF_Bismark", "HL60_RRBS_rep_ENCFF001TNE", "HL60_RRBS_rep_ENCFF001TNF",
            "K562_RRBS_rep_ENCFF001TOL", "K562_RRBS_rep_ENCFF001TOM", "K562_WGBS_rep_ENCFF721JMB", "K562_WGBS_rep_ENCFF721JMB_chr20", "K562_WGBS_rep_ENCFF721JMB_chr20_except", "K562_WGBS_rep_ENCFF721JMB_chr20_except_2", "K562_WGBS_rep_ENCFF867JRG"]
    folders = [
            "APL_BSseq_cut10"]  # , "APL_BSseq_cut5", "APL_oxBSseq_cut10", "APL_oxBSseq_cut5", "HL60_AML_Bsseq_cut5", "HL60_AML_oxBsseq_cut5", "HL60_RRBS_rep_ENCFF000MDA_Bismark", "HL60_RRBS_rep_ENCFF000MDF_Bismark", "HL60_RRBS_rep_ENCFF001TNE", "HL60_RRBS_rep_ENCFF001TNF", "K562_RRBS_rep_ENCFF001TOL", "K562_RRBS_rep_ENCFF001TOM", "K562_WGBS_rep_ENCFF721JMB", "K562_WGBS_rep_ENCFF867JRG"]

    # 'K562_WGBS_joined', 'APL_BSseq_cut10', 'HL60_AML_Bsseq_cut5', 'NA19240_RRBS_joined'
    folders = ["NA19240_RRBS_joined", 'K562_WGBS_joined', 'APL_BSseq_cut10', 'HL60_AML_Bsseq_cut5']

    stat = "corrAll"

    for folder in folders:
        print(folder)
        df = load_all_perf_data_for_dataset(folder)

        # indir = os.path.join(nanocompare_basedir, 'reports', folder)
        # data = pp.load_data("/home/rosikw/li-lab/NanoporeData/WR_ONT_analyses/NanoCompare/reports/{}".format(folder))
        # df = pp.load_data(indir)

        logger.debug(f"df={df}")

        # data.to_csv("{}.combined.tsv".format(folder), sep='\t', index=False)

        #######

        plt.clf()

        # df = pd.read_csv("{}.combined.tsv".format(folder), delimiter="\t")
        fig = plt.gcf()
        fig.set_size_inches(4, 4)
        plt.rcParams.update({'font.size': 14})
        # sns.boxplot(x="method", y="AUC", hue="BinaryLabels", data=df, palette="Set1")
        # ax = sns.boxplot(x="BasecallTool", y=stat, data=df, palette="Set1", order=["Tombo_calls", "Nanopolish_calls", "DeepSignal_calls", "DeepMod_calls"])

        ax = sns.boxplot(x="Tool", y=stat, data=df, order=tools_abbr)

        # ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        ax.set_xticklabels([], rotation=45)

        plt.ylim(0, 1)

        title_str = get_simple_title_from_ds(folder)
        plt.title(title_str)

        outfn = os.path.join(pic_base_dir, f"{folder}.{stat}.time.{current_time_str()}.BoxPlot.png")
        plt.savefig(outfn, bbox_inches='tight', dpi=600, format="png")
        logger.info(f"save to {outfn}")
        plt.show()

        # break

    stat = "corrMix"

    for folder in folders:
        print(folder)
        df = load_all_perf_data_for_dataset(folder)

        plt.clf()

        fig = plt.gcf()
        fig.set_size_inches(4, 4)
        plt.rcParams.update({'font.size': 14})

        ax = sns.boxplot(x="Tool", y=stat, data=df, order=tools_abbr)
        # ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        ax.set_xticklabels([], rotation=45)

        title_str = get_simple_title_from_ds(folder)

        plt.ylim(0, 1)
        plt.title(title_str)

        current_palette = sns.color_palette()
        pal_plot = [mpatches.Patch(color=current_palette[i], label=tools_abbr[i]) for i in range(4)]
        plt.legend(handles=pal_plot, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., title='Tool')

        outfn = os.path.join(pic_base_dir, f"{folder}.{stat}.time.{current_time_str()}.BoxPlot.png")
        plt.savefig(outfn, bbox_inches='tight', dpi=600, format="png")
        logger.info(f"save to {outfn}")
        plt.show()
        # break

    pass


def plot_runnnig_time_and_mem_usage():
    df = load_running_time_and_mem_usage()

    pal_plot = get_pal_4()

    set_style(font_scale=1.5)
    sns.set_style('ticks')
    # fig, ax = plt.subplots()
    fig = plt.gcf()
    fig.set_size_inches(15, 4)
    # plt.rcParams.update({'font.size': 18})

    # Subplot 1
    plt.subplot(1, 2, 1)

    ax1 = sns.barplot(x="mem", y="tool", data=df, order=tools_abbr)

    ax1.set(xlabel='RAM memory used (GB)', ylabel='')
    sns.despine()
    plt.tight_layout()

    # Subplot 2
    plt.subplot(1, 2, 2)
    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25, wspace=0.35)
    ax2 = sns.barplot(x="time", y="tool", data=df, order=tools_abbr)

    plt.locator_params(axis='x', nbins=4)
    plt.ylabel("")
    plt.xlabel("Total CPU time consumed (seconds)")
    sns.despine()

    plt.legend(handles=pal_plot, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., title='Tool')

    plt.tight_layout()

    outfn = os.path.join(pic_base_dir, f"nanocompare_resources_usage_{current_time_str()}.png")
    plt.savefig(outfn, dpi=600, bbox_inches='tight', format="png")
    logger.info(f"save to {outfn}")

    plt.show()


def get_df_from_gen_figure_3a():
    ds_list4 = ['K562_WGBS_joined', 'APL_BSseq_cut10', 'HL60_AML_Bsseq_cut5', 'NA19240_RRBS_joined']

    df = get_performance_from_datasets_and_locations(ds_list=ds_list4, location_list=locations_category + locations_singleton)

    outfn = os.path.join(pic_base_dir, "datasets_4_figure_a_data.xlsx")
    df.to_excel(outfn)

    return df

    pass


def gen_figure_2a():
    """
    Scatter plot on FacetGrid
    :return:
    """

    ds_list4 = ['K562_WGBS_joined', 'APL_BSseq_cut10', 'HL60_AML_Bsseq_cut5', 'NA19240_RRBS_joined']

    measure_list = [['F1_5mC', 'F1_5C']]

    # measure_list = [['F1_5mC', 'F1_5C'],
    #         ['accuracy', 'roc_auc'],
    #         ['precision_5mC', 'precision_5C'],
    #         ['recall_5mC', 'recall_5C']]
    #
    # measure_list = [['accuracy', 'roc_auc'],
    #         ['precision_5mC', 'precision_5C'],
    #         ['recall_5mC', 'recall_5C']]

    for meas_list in measure_list:
        # meas_list = ['precision_5mC', 'precision_5C']
        scatter_facet_grid_multiple_ds_5mc_5c_performance(ds_list=ds_list4, location_list=locations_category, meas_list=meas_list)
        scatter_facet_grid_multiple_ds_5mc_5c_performance(ds_list=ds_list4, location_list=locations_singleton, meas_list=meas_list)

    # meas_list = ['precision_5mC', 'precision_5C']
    # scatter_facet_grid_multiple_ds_5mc_5c_performance(ds_list=ds_list4, location_list=locations_category, meas_list=meas_list)
    # scatter_facet_grid_multiple_ds_5mc_5c_performance(ds_list=ds_list4, location_list=locations_singleton, meas_list=meas_list)
    #
    # meas_list = ['recall_5mC', 'recall_5C']
    # scatter_facet_grid_multiple_ds_5mc_5c_performance(ds_list=ds_list4, location_list=locations_category, meas_list=meas_list)
    # scatter_facet_grid_multiple_ds_5mc_5c_performance(ds_list=ds_list4, location_list=locations_singleton, meas_list=meas_list)


def gen_figure_2bc():
    """
    Box plot of all results
    :return:
    """

    metrics = ["F1_5mC", "F1_5C", "accuracy", "roc_auc", 'precision_5mC', 'precision_5C', 'recall_5mC', 'recall_5C']

    # metrics = ["F1_5mC", "F1_5C"]
    metrics = ["accuracy", "roc_auc"]

    box_plots_all_locations(metrics=metrics)


def gen_figure_4a():
    """
    Correlation plots
    :return:
    """
    cor_plot()
    pass


def gen_figure_4b():
    """
    Correlation plots
    :return:
    """
    cor_box_plot()
    pass


def gen_figure_4c():
    """
    Bar plots of running time and mem usage
    :return:
    """
    plot_runnnig_time_and_mem_usage()


def pie_plot_for_ds(dsname="NA19240"):
    df = load_sing_nonsing_count_df()
    #
    df1 = df[df['dsname'] == dsname]
    #
    logger.debug(f"df1={df1}")
    #
    nsing = df1[df1['location'].isin(['absolute'])]['count'].sum()
    ncond = df1[df1['location'] == 'concordant']['count'].sum()
    ndisc = df1[df1['location'] == 'discordant']['count'].sum()

    # df = load_count_ds_original()
    #
    # nsing = df.loc[dsname, ('singletons', 'total.sites')]
    # ncond = df.loc[dsname, ('concordant', 'total.sites')]
    # ndisc = df.loc[dsname, ('discordant', 'total.sites')]

    piedata = [nsing, ncond, ndisc]
    pielabel = ['Singletons', "Concordant", "Discordant"]

    # plot_pie(piedata, pielabel)

    plot_pie_chart(piedata, pielabel, dsname=dsname)

    pass


def pie_plot_all():
    dslist = ['NA19240', 'K562', "HL60", 'APL']

    for dsname in dslist:
        pie_plot_for_ds(dsname=dsname)


# def plot_pie(data, labels):
#     # explode = (0, 0, 0, 0.1, 0, 0)
#     plt.pie(data, labels=labels, autopct='%1.1f%%', shadow=False, startangle=150)
#     plt.title("Pie chart")
#     plt.show()


def plot_pie_chart(data, labels, dsname="NA19240"):
    set_style(font_scale=1.0)
    fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))

    percent = np.array(data) / np.sum(data) * 100

    logger.debug(f"percent={percent}")

    labels_legend = [f"{labels[k]}: {percent[k]:.1f}%" for k in range(len(labels))]

    # wedges, texts = ax.pie(data)
    # wedges, texts = ax.pie(data, wedgeprops=dict(width=0.5), startangle=-40)

    explode = (0, 0.1, 0.1)  # only "explode" the 2nd slice (i.e. 'Hogs')

    wedges, texts = ax.pie(data, explode=explode, labels=data, startangle=90)

    if False:
        bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
        kw = dict(arrowprops=dict(arrowstyle="-"),
                  bbox=bbox_props, zorder=0, va="center")

        for i, p in enumerate(wedges):
            ang = (p.theta2 - p.theta1) / 2. + p.theta1
            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            connectionstyle = "angle,angleA=0,angleB={}".format(ang)
            kw["arrowprops"].update({"connectionstyle": connectionstyle})
            ax.annotate(f"{percent[i]:.1f}%", xy=(x, y), xytext=(1.35 * np.sign(x), 1.4 * y),
                        horizontalalignment=horizontalalignment, **kw)

    # ax.set_title("Matplotlib bakery: A donut")
    ax.legend(wedges, labels_legend,
              title="",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1))

    ax.set_title(f"{dsname}")

    # plt.legend(wedges, labels_legend, loc="lower left")

    ax.figure.tight_layout()
    outfn = os.path.join(pic_base_dir, f"pie_plot_{dsname}_time_{current_time_str()}.png")
    ax.figure.savefig(outfn, format='png', dpi=600)

    logger.info(f"save to {outfn}")

    plt.show()


if __name__ == '__main__':
    set_log_debug_level()

    gen_figure_2a()


    # pie_plot_all()
    # gen_figure_2bc()

    # df = load_all_perf_data_for_dataset_list()
    # gen_figure_2ac()
    #

    # df1 = load_box_plot_all_data()
    # logger.debug(f"df1 = {df1}")
    #
    # outfn=os.path.join(pic_base_dir, "df1.xlsx")
    # df1.to_excel(outfn)
    #
    #
    # df2 = load_all_perf_data_for_dataset_list()
    # logger.debug(f"df2 = {df2}")
    #
    # outfn=os.path.join(pic_base_dir, "df2.xlsx")
    # df2.to_excel(outfn)

    # gen_figure_2bd()

    # gen_figure_2a()
    # gen_figure_2bc()
    # gen_figure_3a()
    # gen_figure_3b()
    # smooth_scatter_cor_plot()

    # box_plots_all_locations()
    # box_plots_all_locations()

    # df = get_df_from_gen_figure_3a()

    # cor_box_plot()
    #
    # alldf = load_all_perf_data()
    #
    # df1 = load_all_perf_data_for_dataset('APL_BSseq_cut10')
