from __future__ import annotations

import pandas as pd
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes

SOFT_BLUE = "#9DCAE8"
SOFT_TEAL = "#A7D8D0"
SOFT_LAVENDER = "#C8C7E8"
SOFT_MINT = "#BFE3C0"
SOFT_SKY = "#D6EEF8"
MUTED_BLUE = "#4F8FB3"
SOFT_PALETTE = [SOFT_BLUE, SOFT_TEAL, SOFT_LAVENDER, SOFT_MINT]


def _finalize_axes(ax: Axes, *, title: str, xlabel: str, ylabel: str) -> Axes:
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.figure.tight_layout()
    return ax


def plot_matches_by_season(
    data: pd.DataFrame,
    *,
    season_column: str = "season",
    count_column: str = "match_count",
    title: str = "Số trận theo mùa giải",
) -> Axes:
    """Plot match counts by season."""
    import matplotlib.pyplot as plt

    _, ax = plt.subplots(figsize=(9, 4))
    ax.bar(data[season_column], data[count_column], color=SOFT_BLUE)
    ax.tick_params(axis="x", rotation=45)
    for label in ax.get_xticklabels():
        label.set_ha("right")
    return _finalize_axes(ax, title=title, xlabel="Mùa giải", ylabel="Số trận")


def plot_matches_by_league(
    data: pd.DataFrame,
    *,
    league_column: str = "league_name",
    count_column: str = "match_count",
    title: str = "Số trận theo giải đấu",
) -> Axes:
    """Plot match counts by league as a horizontal bar chart."""
    import matplotlib.pyplot as plt

    plot_data = data.sort_values(count_column)
    _, ax = plt.subplots(figsize=(9, 5))
    ax.barh(plot_data[league_column], plot_data[count_column], color=SOFT_TEAL)
    return _finalize_axes(ax, title=title, xlabel="Số trận", ylabel="Giải đấu")


def plot_goal_histogram(
    series: pd.Series,
    *,
    title: str = "Phân bố tổng bàn thắng mỗi trận",
    xlabel: str = "Tổng bàn thắng",
) -> Axes:
    """Plot a histogram for goal counts."""
    import matplotlib.pyplot as plt

    _, ax = plt.subplots(figsize=(8, 4))
    bins = range(0, int(series.max()) + 2)
    ax.hist(series, bins=bins, color=SOFT_BLUE, edgecolor="white")
    return _finalize_axes(ax, title=title, xlabel=xlabel, ylabel="Số trận")


def plot_goal_boxplot(
    data: pd.DataFrame,
    columns: list[str],
    labels: list[str],
    *,
    title: str = "Boxplot bàn thắng",
) -> Axes:
    """Plot a boxplot for selected goal columns."""
    import matplotlib.pyplot as plt

    _, ax = plt.subplots(figsize=(7, 4))
    boxplot = ax.boxplot(
        [data[column] for column in columns],
        tick_labels=labels,
        patch_artist=True,
    )
    for patch, color in zip(boxplot["boxes"], SOFT_PALETTE, strict=False):
        patch.set_facecolor(color)
        patch.set_edgecolor(MUTED_BLUE)
    for median in boxplot["medians"]:
        median.set_color(MUTED_BLUE)
    return _finalize_axes(ax, title=title, xlabel="", ylabel="Số bàn thắng")


def plot_match_result_distribution(
    data: pd.DataFrame,
    *,
    result_column: str = "result",
    rate_column: str = "rate_pct",
    title: str = "Tỷ lệ Home Win, Draw, Away Win",
) -> Axes:
    """Plot match result percentages."""
    import matplotlib.pyplot as plt

    _, ax = plt.subplots(figsize=(6, 4))
    colors = [SOFT_BLUE, SOFT_SKY, SOFT_TEAL]
    ax.bar(data[result_column], data[rate_column], color=colors[: len(data)])
    return _finalize_axes(ax, title=title, xlabel="Kết quả", ylabel="Tỷ lệ (%)")


def plot_average_goals_by_season(
    data: pd.DataFrame,
    *,
    season_column: str = "season",
    value_column: str = "avg_total_goals",
    title: str = "Bàn thắng trung bình mỗi trận theo mùa",
) -> Axes:
    """Plot average goals per match by season."""
    import matplotlib.pyplot as plt

    _, ax = plt.subplots(figsize=(9, 4))
    ax.plot(
        data[season_column],
        data[value_column],
        marker="o",
        color=MUTED_BLUE,
        markerfacecolor=SOFT_BLUE,
    )
    ax.tick_params(axis="x", rotation=45)
    for label in ax.get_xticklabels():
        label.set_ha("right")
    return _finalize_axes(
        ax,
        title=title,
        xlabel="Mùa giải",
        ylabel="Bàn thắng trung bình",
    )


def plot_team_attribute_distribution(
    dataframe: pd.DataFrame,
    columns: list[str],
    labels: list[str],
    *,
    title: str = "Phân bố một số thuộc tính đội",
) -> Axes:
    """Plot a boxplot for selected team attribute columns."""
    import matplotlib.pyplot as plt

    _, ax = plt.subplots(figsize=(8, 4))
    boxplot = ax.boxplot(
        [dataframe[column].dropna() for column in columns],
        tick_labels=labels,
        patch_artist=True,
    )
    for patch, color in zip(boxplot["boxes"], SOFT_PALETTE, strict=False):
        patch.set_facecolor(color)
        patch.set_edgecolor(MUTED_BLUE)
    for median in boxplot["medians"]:
        median.set_color(MUTED_BLUE)
    return _finalize_axes(ax, title=title, xlabel="", ylabel="Điểm thuộc tính")
