
.. ipython:: python
   :suppress:

   import numpy as np
   import pandas as pd
   import matplotlib as mpl
   import matplotlib.pyplot as plt
   import seaborn as sns

   plt.style.use('default')
   mpl.rcParams['axes.labelsize'] = 'large'
   mpl.rcParams['savefig.bbox'] = 'tight'
   mpl.rcParams['savefig.pad_inches'] = 0.1

   pd.options.display.max_rows = 15

============
Recall order
============

A key advantage of free recall is that it provides information not only about
what items are recalled, but also the order in which they are recalled. A
number of analyses have been developed to charactize different influences on
recall order, such as the temporal order in which the items were presented at
study, the category of the items themselves, or the semantic similarity between
pairs of items.

Each conditional response probability (CRP) analysis involves calculating the
probability of some type of transition event. For the lag-CRP analysis,
transition events of interest are the different lags between serial positions
of items recalled adjacent to one another. Similar analyses focus not on
the serial position in which items are presented, but the properties of the
items themselves. A semantic-CRP analysis calculates the probability of
transitions between items in different semantic relatedness bins. A special
case of this analysis is when item pairs are placed into one of two bins,
depending on whether they are in the same stimulus category or not. In Psifr,
this is referred to as a category-CRP analysis.

Lag-CRP
~~~~~~~

In all CRP analyses, transition probabilities are calculated conditional
on a given transition being available :cite:p:`Kahana:1996`. For example, in a six-item list,
if the items 6, 1, and 4 have been recalled, then possible items that could
have been recalled next are 2, 3, or 5; therefore, possible lags at
that point in the recall sequence are -2, -1, or +1. The number of actual
transitions observed for each lag is divided by the number of times that
lag was possible, to obtain the CRP for each lag.

First, load some sample data and create a merged DataFrame:

.. ipython:: python

    from psifr import fr
    df = fr.sample_data('Morton2013')
    data = fr.merge_free_recall(df, study_keys=['category'])

Next, call :py:func:`~psifr.fr.lag_crp` to calculate conditional response
probability as a function of lag.

.. ipython:: python

    crp = fr.lag_crp(data)
    crp

The results show the count of times a given transition actually happened
in the observed recall sequences (:code:`actual`) and the number of times a
transition could have occurred (:code:`possible`). Finally, the :code:`prob` column
gives the estimated probability of a given transition occurring, calculated
by dividing the actual count by the possible count.

Use :py:func:`~psifr.fr.plot_lag_crp` to display the results:

.. ipython:: python

   @savefig lag_crp.svg
   g = fr.plot_lag_crp(crp)

The peaks at small lags (e.g., +1 and -1) indicate that the recall sequences
show evidence of a temporal contiguity effect; that is, items presented near
to one another in the list are more likely to be recalled successively than
items that are distant from one another in the list.

Compound lag-CRP
~~~~~~~~~~~~~~~~

The compound lag-CRP was developed to measure how temporal clustering
changes as a result of prior clustering during recall :cite:p:`Lohnas:2014`.
They found evidence that temporal clustering is greater immediately after
transitions with short lags compared to long lags. The :py:func:`~psifr.fr.lag_crp_compound`
analysis calculates conditional response probability by lag, but with the
additional condition of the lag of the previous transition.

.. ipython:: python

    crp = fr.lag_crp_compound(data)
    crp

The results show conditional response probabilities as in the standard
lag-CRP analysis, but with two lag columns: :code:`previous` (the lag
of the prior transition) and :code:`current` (the lag of the current
transition).

This is a lot of information, and the sample size for many bins is very
small. Following :cite:p:`Lohnas:2014`, we can apply bins to the lag of
the previous transition to increase the sample size in each bin. We
first sum the actual and possible transition counts, and then calculate
the probability of each of the new bins.

.. ipython:: python

    binned = crp.reset_index()
    binned.loc[binned['previous'].abs() > 3, 'Previous'] = '|Lag|>3'
    binned.loc[binned['previous'] == 1, 'Previous'] = 'Lag=+1'
    binned.loc[binned['previous'] == -1, 'Previous'] = 'Lag=-1'
    summed = binned.groupby(['subject', 'Previous', 'current'])[['actual', 'possible']].sum()
    summed['prob'] = summed['actual'] / summed['possible']
    summed

We can then plot the compound lag-CRP using the standard
:py:func:`~psifr.fr.plot_lag_crp` plotting function.

.. ipython:: python

    @savefig lag_crp_compound.svg
    g = fr.plot_lag_crp(summed, lag_key='current', hue='Previous').add_legend()

Note that some lags are considered impossible as they would require
a repeat of a previously recalled item (e.g., a +1 lag followed by a -1
lag is not possible). For both of the adjacent conditions (+1 and -1),
the lag-CRP is sharper compared to the long-lag condition (:math:`| \mathrm{lag} | >3`).
This suggests that there is compound temporal clustering.

Lag rank
~~~~~~~~

We can summarize the tendency to group together nearby items by running a lag
rank analysis :cite:p:`Polyn:2009` using :py:func:`~psifr.fr.lag_rank`.
For each recall, this determines the absolute lag of all
remaining items available for recall and then calculates their percentile
rank. Then the rank of the actual transition made is taken, scaled to vary
between 0 (furthest item chosen) and 1 (nearest item chosen). Chance
clustering will be 0.5; clustering above that value is evidence of a
temporal contiguity effect.

.. ipython:: python

    ranks = fr.lag_rank(data)
    ranks
    ranks.agg(['mean', 'sem'])

Category CRP
~~~~~~~~~~~~

If there are multiple categories or conditions of trials in a list, we
can test whether participants tend to successively recall items from the
same category. The category-CRP, calculated using
:py:func:`~psifr.fr.category_crp`, estimates the probability of successively
recalling two items from the same category :cite:p:`Polyn:2009`.

.. ipython:: python

    cat_crp = fr.category_crp(data, category_key='category')
    cat_crp
    cat_crp[['prob']].agg(['mean', 'sem'])

The expected probability due to chance depends on the number of
categories in the list. In this case, there are three categories, so
a category CRP of 0.33 would be predicted if recalls were sampled
randomly from the list.

Category clustering
~~~~~~~~~~~~~~~~~~~

A number of measures have been developed to measure category clustering
relative to that expected due to chance, under certain assumptions. Two
such measures are list-based clustering (LBC) :cite:p:`Stricker:2002` and adjusted ratio of
clustering (ARC) :cite:p:`Roenker:1971`.

These measures can be calculated using the
:py:func:`~psifr.fr.category_clustering` function.

.. ipython:: python

    clust = fr.category_clustering(data, category_key='category')
    clust.agg(['mean', 'sem'])

Both measures are defined such that positive values indicate above-chance
clustering. ARC scores have a maximum of 1, while the upper
bound of LBC scores depends on the number of categories and the number
of items per category in the study list.

Distance CRP
~~~~~~~~~~~~

While the category CRP examines clustering based on semantic similarity
at a coarse level (i.e., whether two items are in the same category or
not), recall may also depend on more nuanced semantic relationships.

Models of semantic knowledge allow the semantic distance between
pairs of items to be quantified. If you have such a model defined for
your stimulus pool, you can use the distance CRP analysis to examine
how semantic distance affects recall transitions :cite:p:`Howard:2002,Morton:2016`.

You must first define distances between pairs of items. Here, we
use correlation distances based on the wiki2USE model.

.. ipython:: python

    items, distances = fr.sample_distances('Morton2013')

We also need a column indicating the index of each item in the
distances matrix. We use :py:func:`~psifr.fr.pool_index` to create
a new column called :code:`item_index` with the index of each item in
the pool corresponding to the distances matrix.

.. ipython:: python

    data['item_index'] = fr.pool_index(data['item'], items)

Finally, we must define distance bins. Here, we use 10 bins with
equally spaced distance percentiles. Note that, when calculating
distance percentiles, we use the :py:func:`~scipy.spatial.distance.squareform` function to
get only the non-diagonal entries.

.. ipython:: python

    from scipy.spatial.distance import squareform
    edges = np.percentile(squareform(distances), np.linspace(1, 99, 10))

We can now calculate conditional response probability as a function of
distance bin using :py:func:`~psifr.fr.distance_crp`,
to examine how response probability varies with semantic distance.

.. ipython:: python

    dist_crp = fr.distance_crp(data, 'item_index', distances, edges)
    dist_crp

Use :py:func:`~psifr.fr.plot_distance_crp` to display the results:

.. ipython:: python

    @savefig distance_crp.svg
    g = fr.plot_distance_crp(dist_crp).set(ylim=(0, 0.1))

Conditional response probability decreases with increasing semantic
distance, suggesting that recall order was influenced by the semantic
similarity between items. Of course, a complete analysis should address
potential confounds such as the category structure of the list. See
the :ref:`Restricting analysis to specific items <restricting>` section
for an example of restricting analysis based on category.

Distance rank
~~~~~~~~~~~~~

Similarly to the lag rank analysis of temporal clustering, we can
summarize distance-based clustering (such as semantic clustering) with
a single rank measure :cite:p:`Polyn:2009`. The distance rank varies from 0 (the
most-distant item is always recalled) to 1 (the closest item is always
recalled), with chance clustering corresponding to 0.5. Given a matrix
of item distances, we can calculate distance rank using
:py:func:`~psifr.fr.distance_rank`.

.. ipython:: python

    dist_rank = fr.distance_rank(data, 'item_index', distances)
    dist_rank.agg(['mean', 'sem'])

.. _distance_rank_shifted:

Distance rank shifted
~~~~~~~~~~~~~~~~~~~~~

Like with the compound lag-CRP, we can also examine how recalls before
the just-previous one may predict subsequent recalls. To examine whether
distances relative to earlier items are predictive of the next recall,
we can use a shifted distance rank analysis :cite:p:`Morton:2016` using
:py:func:`~psifr.fr.distance_rank_shifted`.

Here, to account for the category structure of the list, we will only
include within-category transitions (see the
:ref:`Restricting analysis to specific items <restricting>` section for details).

.. ipython:: python

    ranks = fr.distance_rank_shifted(
        data, 'item_index', distances, 4, test_key='category', test=lambda x, y: x == y
    )
    ranks

The distance rank is returned for each shift. The -1 shift is the same as
the standard distance rank analysis. We can visualize how distance rank
changes with shift using :py:func:`seaborn.relplot`.

.. ipython:: python

    @savefig distance_rank_shifted.svg
    g = sns.relplot(
        data=ranks.reset_index(), x='shift', y='rank', kind='line', height=3
    ).set(xlabel='Output lag', ylabel='Distance rank', xticks=[-4, -3, -2, -1])

Restricting analysis to specific items
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes you may want to focus an analysis on a subset of recalls. For
example, in order to exclude the period of high clustering commonly
observed at the start of recall, lag-CRP analyses are sometimes
restricted to transitions after the first three output positions.

You can restrict the recalls included in a transition analysis using
the optional :code:`item_query` argument. This is built on the Pandas
query/eval system, which makes it possible to select rows of a
:code:`DataFrame` using a query string. This string can refer to any
column in the data. Any items for which the expression evaluates to
:code:`True` will be included in the analysis.

For example, we can use the :code:`item_query` argument to exclude any
items recalled in the first three output positions from analysis. Note
that, because non-recalled items have no output position, we need to
include them explicitly using :code:`output > 3 or not recall`.

.. ipython:: python

    crp_op3 = fr.lag_crp(data, item_query='output > 3 or not recall')
    @savefig lag_crp_op3.svg
    g = fr.plot_lag_crp(crp_op3)

.. _restricting:

Restricting analysis to specific transitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In other cases, you may want to focus an analysis on a subset of
transitions based on some criteria. For example, if a list contains
items from different categories, it is a good idea to take this into
account when measuring temporal clustering using a lag-CRP analysis
:cite:p:`Polyn:2011,Morton:2017`.
One approach is to separately analyze within- and across-category
transitions.

Transitions can be selected for inclusion using the optional
:code:`test_key` and :code:`test` inputs. The :code:`test_key`
indicates a column of the data to use for testing transitions; for
example, here we will use the :code:`category` column. The
:code:`test` input should be a function that takes in the test value
of the previous recall and the current recall and returns True or False
to indicate whether that transition should be included. Here, we will
use a lambda (anonymous) function to define the test.

.. ipython:: python

    crp_within = fr.lag_crp(data, test_key='category', test=lambda x, y: x == y)
    crp_across = fr.lag_crp(data, test_key='category', test=lambda x, y: x != y)
    crp_combined = pd.concat([crp_within, crp_across], keys=['within', 'across'], axis=0)
    crp_combined.index.set_names('transition', level=0, inplace=True)
    @savefig lag_crp_cat.svg
    g = fr.plot_lag_crp(crp_combined, hue='transition').add_legend()

The :code:`within` curve shows the lag-CRP for transitions between
items of the same category, while the :code:`across` curve shows
transitions between items of different categories.
