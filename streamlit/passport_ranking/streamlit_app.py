import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Passport Ranking Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.dashboard-title {
    font-size: 38px;
    font-weight: 700;
    margin-bottom: 5px;
}

.dashboard-subtitle {
    font-size: 16px;
    color: #777;
    margin-bottom: 25px;
}

.kpi-card {
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #e6e6e6;
    background-color: #ffffff;
    text-align: center;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
}

.kpi-title {
    font-size: 14px;
    color: #666;
}

.kpi-value {
    font-size: 27px;
    font-weight: 700;
    margin-top: 5px;
}

.section-title {
    font-size: 24px;
    font-weight: 650;
    margin-top: 20px;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="dashboard-title">'
    '🌍 Passport Ranking Dashboard'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Compare passport strength, country access and historical performance'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# SNOWFLAKE SESSION
# =========================================================

session = get_active_session()


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data(ttl=300)
def load_data():

    query = """
    SELECT
        COUNTRY_NAME,
        RNK,
        ACCESS_NO_COUNTRY,
        YRS
    FROM SHPROD.PUBLIC.RANK_PASSPORT
    ORDER BY YRS, RNK
    """

    data = session.sql(query).to_pandas()

    data.columns = data.columns.str.upper()

    return data


df = load_data()


# =========================================================
# DATA VALIDATION
# =========================================================

if df.empty:

    st.warning(
        "No passport ranking data available."
    )

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🎛️ Dashboard Controls")

st.sidebar.markdown("---")


# =========================================================
# YEAR SELECTION
# =========================================================

years = sorted(
    df["YRS"].dropna().unique(),
    reverse=True
)

selected_year = st.sidebar.selectbox(
    "📅 Select Year",
    years
)


# =========================================================
# TOP N SELECTION
# =========================================================

top_n = st.sidebar.slider(
    "🏆 Top Countries",
    min_value=5,
    max_value=30,
    value=10,
    step=5
)


# =========================================================
# MULTI-COUNTRY SELECTION
# =========================================================

all_countries = sorted(
    df["COUNTRY_NAME"]
    .dropna()
    .unique()
)

selected_countries = st.sidebar.multiselect(
    "🆚 Compare Countries",
    options=all_countries,
    default=[],
    max_selections=10,
    help="Select 2 or more countries to compare."
)


# =========================================================
# YEAR COMPARISON
# =========================================================

compare_years = st.sidebar.multiselect(
    "📈 Compare Years",
    options=years,
    default=[selected_year],
    help="Select multiple years for historical comparison."
)


# =========================================================
# CURRENT YEAR DATA
# =========================================================

current_df = df[
    df["YRS"] == selected_year
].copy()

current_df = current_df.sort_values(
    "RNK"
)


# =========================================================
# KPI CALCULATIONS
# =========================================================

total_countries = len(
    current_df
)

best_rank = int(
    current_df["RNK"].min()
)

max_access = int(
    current_df["ACCESS_NO_COUNTRY"].max()
)

avg_access = round(
    current_df["ACCESS_NO_COUNTRY"].mean(),
    1
)


# =========================================================
# KPI CARDS
# =========================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">
                🌎 Countries
            </div>
            <div class="kpi-value">
                {total_countries}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">
                🏆 Best Rank
            </div>
            <div class="kpi-value">
                #{best_rank}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">
                🌍 Maximum Access
            </div>
            <div class="kpi-value">
                {max_access}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col4:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">
                📊 Average Access
            </div>
            <div class="kpi-value">
                {avg_access}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# TOP PASSPORT RANKINGS
# =========================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">'
    '🏆 Top Passport Rankings'
    '</div>',
    unsafe_allow_html=True
)


top_df = current_df.head(
    top_n
)


ranking_chart = top_df[
    [
        "COUNTRY_NAME",
        "RNK"
    ]
].set_index(
    "COUNTRY_NAME"
)


st.bar_chart(
    ranking_chart,
    horizontal=True,
    height=450
)


st.caption(
    f"Top {top_n} passport rankings for {selected_year}"
)


# =========================================================
# PASSPORT ACCESS
# =========================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">'
    '🌍 Countries With Highest Access'
    '</div>',
    unsafe_allow_html=True
)


access_df = current_df.sort_values(
    "ACCESS_NO_COUNTRY",
    ascending=False
).head(
    top_n
)


access_chart = access_df[
    [
        "COUNTRY_NAME",
        "ACCESS_NO_COUNTRY"
    ]
].set_index(
    "COUNTRY_NAME"
)


st.bar_chart(
    access_chart,
    horizontal=True,
    height=450
)


st.caption(
    f"Countries with highest visa-free / accessible destinations in {selected_year}"
)


# =========================================================
# COUNTRY COMPARISON
# =========================================================

if len(selected_countries) >= 2:

    st.markdown("---")

    st.markdown(
        '<div class="section-title">'
        '🆚 Country Comparison'
        '</div>',
        unsafe_allow_html=True
    )


    comparison_df = current_df[
        current_df["COUNTRY_NAME"].isin(
            selected_countries
        )
    ].copy()


    comparison_df = comparison_df.sort_values(
        "RNK"
    )


    # -----------------------------------------------------
    # COUNTRY METRICS
    # -----------------------------------------------------

    metric_count = min(
        len(selected_countries),
        5
    )


    metric_columns = st.columns(
        metric_count
    )


    for i, country in enumerate(
        selected_countries
    ):

        country_data = comparison_df[
            comparison_df["COUNTRY_NAME"] == country
        ]


        if country_data.empty:
            continue


        row = country_data.iloc[0]


        with metric_columns[
            i % metric_count
        ]:

            st.metric(
                country,
                f"Rank #{int(row['RNK'])}",
                f"{int(row['ACCESS_NO_COUNTRY'])} access"
            )


    # -----------------------------------------------------
    # RANK COMPARISON
    # -----------------------------------------------------

    st.subheader(
        f"🏆 Ranking Comparison — {selected_year}"
    )


    rank_compare = comparison_df[
        [
            "COUNTRY_NAME",
            "RNK"
        ]
    ].set_index(
        "COUNTRY_NAME"
    )


    st.bar_chart(
        rank_compare,
        horizontal=True,
        height=350
    )


    st.caption(
        "Lower rank number represents a stronger passport."
    )


    # -----------------------------------------------------
    # ACCESS COMPARISON
    # -----------------------------------------------------

    st.subheader(
        f"🌍 Access Comparison — {selected_year}"
    )


    access_compare = comparison_df[
        [
            "COUNTRY_NAME",
            "ACCESS_NO_COUNTRY"
        ]
    ].set_index(
        "COUNTRY_NAME"
    )


    st.bar_chart(
        access_compare,
        horizontal=True,
        height=350
    )


    # -----------------------------------------------------
    # COMPARISON TABLE
    # -----------------------------------------------------

    st.subheader(
        "📋 Comparison Table"
    )


    comparison_display = comparison_df[
        [
            "COUNTRY_NAME",
            "RNK",
            "ACCESS_NO_COUNTRY",
            "YRS"
        ]
    ]


    st.dataframe(
        comparison_display,
        use_container_width=True,
        hide_index=True
    )


elif len(selected_countries) == 1:

    st.markdown("---")

    st.info(
        "👆 Select at least 2 countries "
        "from the sidebar to enable comparison."
    )


# =========================================================
# HISTORICAL COUNTRY COMPARISON
# =========================================================

if len(selected_countries) >= 2:

    st.markdown("---")

    st.markdown(
        '<div class="section-title">'
        '📈 Historical Country Comparison'
        '</div>',
        unsafe_allow_html=True
    )


    historical_df = df[
        df["COUNTRY_NAME"].isin(
            selected_countries
        )
    ].copy()


    historical_df = historical_df.sort_values(
        "YRS"
    )


    # =====================================================
    # ACCESS OVER TIME — LINE GRAPH
    # =====================================================

    st.subheader(
        "🌍 Access Over Time"
    )


    access_history = historical_df.pivot(
        index="YRS",
        columns="COUNTRY_NAME",
        values="ACCESS_NO_COUNTRY"
    )


    access_history = access_history.sort_index()


    st.line_chart(
        access_history,
        height=450
    )


    st.caption(
        "📈 Each line represents the number of accessible "
        "countries for the selected passport."
    )


    # =====================================================
    # RANKING OVER TIME — LINE GRAPH
    # =====================================================

    st.subheader(
        "🏆 Ranking Over Time"
    )


    rank_history = historical_df.pivot(
        index="YRS",
        columns="COUNTRY_NAME",
        values="RNK"
    )


    rank_history = rank_history.sort_index()


    st.line_chart(
        rank_history,
        height=450
    )


    st.caption(
        "📈 Lower rank indicates a stronger passport."
    )


# =========================================================
# YEAR COMPARISON
# =========================================================

if len(compare_years) >= 2:

    st.markdown("---")

    st.markdown(
        '<div class="section-title">'
        '📅 Year Comparison'
        '</div>',
        unsafe_allow_html=True
    )


    year_df = df[
        df["YRS"].isin(
            compare_years
        )
    ]


    # -----------------------------------------------------
    # AVERAGE ACCESS BY YEAR
    # -----------------------------------------------------

    st.subheader(
        "🌍 Average Passport Access"
    )


    year_access = (
        year_df
        .groupby("YRS")[
            "ACCESS_NO_COUNTRY"
        ]
        .mean()
        .sort_index()
    )


    st.line_chart(
        year_access,
        height=350
    )


    # -----------------------------------------------------
    # AVERAGE RANK BY YEAR
    # -----------------------------------------------------

    st.subheader(
        "🏆 Average Passport Ranking"
    )


    year_rank = (
        year_df
        .groupby("YRS")[
            "RNK"
        ]
        .mean()
        .sort_index()
    )


    st.line_chart(
        year_rank,
        height=350
    )


# =========================================================
# COMPLETE DATA
# =========================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">'
    '📋 Complete Ranking Data'
    '</div>',
    unsafe_allow_html=True
)


display_df = current_df[
    [
        "COUNTRY_NAME",
        "RNK",
        "ACCESS_NO_COUNTRY",
        "YRS"
    ]
]


st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "🌍 Passport Ranking Project @ Snowflake Interactive Streamlit Dashboard"
)