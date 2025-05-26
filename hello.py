import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from preswald import connect,get_df,query, table,text, plotly

df = get_df("amazon")

text("# ✨ Amazon Popular Books Dataset Dashboard")
text("A comprehensive and interactive analysis of the most popular books available on Amazon.")
text("This dashboard explores a range of metrics such as ratings, pricing, authorship, and publishing trends to uncover insightful patterns and trends across thousands of popular titles.")

text("## Raw Data")
text("Explore the complete dataset including rankings, ratings, price, and other metadata for each book.")
table(df, title="All Rows")


text("## Filtered Data")
text("Removed duplicate titles by selecting the book with the minimum rank per title and replace null brands with 'Unknown'.")
sql_query = """
    SELECT
      Title,
      Rank,
      Rating,
      Total_Ratings,
      Price,
      Genre,
      Manufacturer,
      CASE WHEN Brand IS NULL THEN 'Unknown' ELSE Brand END AS Brand,
      Author,
      "Number of Pages"
    FROM amazon
    WHERE Rank = (
      SELECT MIN(Rank)
      FROM amazon AS a2
      WHERE a2.Title = amazon.Title
    )
    """

filtered_df = query(sql_query, "amazon")

table(filtered_df, title="Filtered Data")

text("## Plot 1: Distribution of Book Ratings")
text("Understand how user ratings are distributed across books. Most popular books tend to cluster around high ratings, showing general customer satisfaction.")
book_ctr= query("""
SELECT Rating, COUNT(*) AS Book_Count
FROM amazon
WHERE Rating IS NOT NULL
  AND Rank = (
    SELECT MIN(Rank)
    FROM amazon AS a2
    WHERE a2.Title = amazon.Title
  )
GROUP BY Rating
ORDER BY Rating DESC
"""
, "amazon")
fig1 = px.histogram(
    book_ctr,
    x="Rating",
    y="Book_Count",
    title="Number of Books by Exact Rating",
    labels={"Rating": "Book Rating", "Book_Count": "Number of Books"},
)
plotly(fig1)

text("## Plot 2: Pages vs Price")
text("Is there a relationship between book size and pricing? This heatmap reveals how the number of pages correlates with pricing, helping identify price-to-content sweet spots.")
fig2 = px.density_heatmap(
    filtered_df,
    x="Number of Pages",
    y="Price",
    nbinsx=30,
    nbinsy=30,
    title="Density (Pages vs Price) for Books with Known Page Count",
    labels={"Number of Pages": "Pages", "Price": "Price (USD)"}
)
plotly(fig2)

text("## Plot 3: Top 10 Most Rated Books")
text("Which titles received the most attention? These are the books with the highest number of user ratings, a good proxy for popularity and sales volume.")
top_books = query("""
SELECT Title, MAX("Total_Ratings") AS Total_Ratings
FROM amazon
WHERE "Total_Ratings" IS NOT NULL
GROUP BY Title
ORDER BY Total_Ratings DESC
LIMIT 10
""", "amazon")
fig3 = px.bar(top_books, y="Title", x="Total_Ratings", orientation="h", title="Top 10 Most Rated Books")
plotly(fig3)

text("## Plot 4: Top 10 Authors by Total Ratings")
text("Which authors are leading in terms of reader engagement? This view aggregates total ratings by author.")
filtered_df["Total_Ratings"] = pd.to_numeric(filtered_df["Total_Ratings"], errors="coerce")

top_authors = filtered_df[filtered_df["Author"].notna()].groupby("Author")["Total_Ratings"].sum().nlargest(10).reset_index()
fig4 = px.bar(top_authors, y="Author", x="Total_Ratings", orientation="h", title="Top 10 Authors by Total Ratings",color="Total_Ratings", color_continuous_scale="RdBu_r")
plotly(fig4)

text("## Plot 5: Top 10 Brands by Total Ratings")
text("Discover which publishing brands dominate the market in terms of user engagement and popularity.")
top_brands = filtered_df[filtered_df["Brand"].notna()].groupby("Brand")["Total_Ratings"].sum().nlargest(10).reset_index()
fig5 = px.bar(top_brands, x="Total_Ratings", y="Brand", orientation="h",
title="Top 10 Brands by Total Ratings", color="Total_Ratings",color_continuous_scale="Plasma")
plotly(fig5)

text("## Plot 6: Top 10 Genres by Total Ratings")
text("What genres do readers prefer? Here's a look at which genres accumulate the most total ratings.")
top_genres = filtered_df[filtered_df["Genre"].notna()].groupby("Genre")["Total_Ratings"].sum().nlargest(10).reset_index()
fig6 = px.bar(top_genres, x="Total_Ratings", y="Genre", orientation="h",title="Top 10 Genres by Total Ratings", color="Total_Ratings",color_continuous_scale="Viridis")
plotly(fig6)

text("## Plot 7: Price Distribution by Genre (Violin Plot)")
text("See how price varies across different genres. Some genres are priced significantly higher due to niche content or collector's value.")
fig7 = px.violin(
    filtered_df,
    x="Genre",
    y="Price",
    title="Price Distribution by Genre (Violin Plot)",
    labels={"Genre": "Genre", "Price": "Price (USD)"},
    box=True,
    points="all"
)
plotly(fig7)

text("## Plot 8: Correlation Heatmap of Numerical Features")
text("This heatmap shows how numerical attributes relate to each other, such as whether higher-rated books also tend to have more pages or cost more.")
numeric_df = filtered_df[["Rating", "Price", "Total_Ratings", "Number of Pages"]].dropna()
corr_matrix = numeric_df.corr()
fig_corr = ff.create_annotated_heatmap(
    z=corr_matrix.values,
    x=list(corr_matrix.columns),
    y=list(corr_matrix.index),
    annotation_text=corr_matrix.round(2).values,
    colorscale="RdBu",
    showscale=True
)
plotly(fig_corr)

text("## Plot 9: Rating vs Price Scatter Plot")
text("Explore how price and rating correlate, color-coded by genre. Some genres show strong positive correlation between price and user satisfaction.")

fig_rating_price = px.scatter(
    filtered_df, x="Price", y="Rating", color="Genre",
    title="Rating vs Price Colored by Genre",
    hover_data=["Title", "Author"],
    labels={"Price": "Price (USD)", "Rating": "Book Rating"}
)
plotly(fig_rating_price)

text("## Plot 10: Top 10 Manufacturers by Total Ratings")
text("Who publishes the books people love most? This ranking highlights the most influential manufacturers by rating counts.")
top_manufacturers = filtered_df[filtered_df["Manufacturer"].notna()] .groupby("Manufacturer")["Total_Ratings"].sum().nlargest(10).reset_index()

fig_mfg = px.bar(
    top_manufacturers, x="Total_Ratings", y="Manufacturer", orientation="h",
    title="Top 10 Manufacturers by Total Ratings", color="Total_Ratings", color_continuous_scale="Sunset"
)
plotly(fig_mfg)

text("## Plot 11: Rating Distribution of Top 5 Brands")
text("Comparing how customer ratings vary across the five most represented brands. Outliers and consistent performers both stand out clearly.")
top_5_brands = filtered_df["Brand"].value_counts().head(5).index
top_brand_df = filtered_df[filtered_df["Brand"].isin(top_5_brands)]

fig_brand_rating = px.box(
    top_brand_df,
    x="Brand",
    y="Rating",
    title="Ratings Distribution for Top 5 Brands",
    points="all",
    color="Brand"
)
plotly(fig_brand_rating)

text("## Plot 13: Treemap of Author Contributions by Total Ratings")
text("The most impactful authors at a glance: the size of each block represents the total number of ratings received across all their books.")
author_ratings = filtered_df[filtered_df["Author"].notna()] \
    .groupby("Author")["Total_Ratings"].sum().reset_index()

fig_treemap = px.treemap(
    author_ratings.sort_values("Total_Ratings", ascending=False).head(50),
    path=["Author"],
    values="Total_Ratings",
    title="Top Authors by Total Ratings (Treemap)"
)
plotly(fig_treemap)

text("---")
text("### 📅 Dataset Overview")
text(f"""
- **Books Analyzed**: {format(len(filtered_df))}
- **Unique Authors**: {format(filtered_df['Author'].nunique())}
- **Genres Covered**: {format(filtered_df['Genre'].nunique())}""")


text("### 💡 Key Insights")
text("""
- High-rated books dominate the dataset, with most ratings clustering above 4.0.
- Price does not necessarily correlate with better ratings.
- Certain authors and genres consistently receive more engagement.
- The 'Unknown' brand still accounts for a considerable share, suggesting either indie or self-published works.
- Many books show strong clustering by price and page count, offering potential pricing strategies for publishers.""")
text("### 📖 Thank you for exploring! Dive deeper by sorting and filtering above visualizations to uncover trends hidden in plain sight.")
