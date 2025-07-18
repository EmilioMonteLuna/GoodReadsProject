""" 
BookVoyage: Personal Reading Discovery Tool
Maven Bookshelf Challenge 2025
A custom book recommendation engine built with Goodreads data
"""

import pandas as pd
import streamlit as st
import re
import os
import urllib.request
import sys

# ===============================================================================
# CONFIGURATION
# ===============================================================================

st.set_page_config(
    page_title="BookVoyage: Your Personal Reading Discovery",
    page_icon="https://img.icons8.com/arcade/64/book.png",
    layout="wide"
)

# ===============================================================================
# DATA LOADING
# ===============================================================================

@st.cache_data(ttl=3600)
def load_works_data():
    """Load only the works dataset for faster startup."""
    try:
        works = pd.read_csv('Data/goodreads_works.csv', low_memory=False)
        return works
    except Exception as e:
        st.error(f"❌ Error loading works data: {e}")
        st.stop()

@st.cache_data(ttl=3600)
def load_reviews_data(use_full=False):
    """Load a sample or the full reviews dataset."""
    if use_full:
        FULL_PATH = "Data/goodreads_reviews.csv"
        if not os.path.exists(FULL_PATH):
            st.error("❌ Full reviews file not found. Please upload 'goodreads_reviews.csv' to the Data folder.")
            return None
        st.warning("⚠️ Loading the full reviews dataset may crash your browser or app if you do not have enough memory (1.3GB+ file). Proceed with caution!")
        path = FULL_PATH
    else:
        SAMPLE_PATH = "Data/goodreads_reviews_sample.csv"
        if not os.path.exists(SAMPLE_PATH):
            st.error("❌ Sample reviews file not found. Please upload 'goodreads_reviews_sample.csv' to the Data folder.")
            return None
        path = SAMPLE_PATH

    try:
        essential_columns = ['work_id', 'rating', 'review_text', 'n_votes']
        reviews = pd.read_csv(path, low_memory=False, usecols=essential_columns)
        required_columns = ['work_id', 'rating', 'review_text']
        missing_columns = [col for col in required_columns if col not in reviews.columns]
        if missing_columns:
            st.error(f"❌ Reviews file is missing columns: {missing_columns}")
            return None
        return reviews
    except Exception as e:
        st.error(f"❌ Error loading reviews: {e}")
        return None

# Load only works data initially for faster startup
with st.spinner("📚 Loading book data..."):
    works_df = load_works_data()

# Initialize reviews_df as None - will be loaded when needed
if 'reviews_df' not in st.session_state:
    st.session_state.reviews_df = None

st.sidebar.success("✅ Basic data loaded successfully!")

# ===============================================================================
# HELPER FUNCTIONS
# ===============================================================================

@st.cache_data(ttl=3600)
def extract_all_genres(df):
    """Extract all unique genres from the dataset."""
    genres_set = set()
    df['genres'] = df['genres'].fillna('')
    
    for genres in df['genres']:
        for g in genres.split(','):
            g = g.strip()
            if g:
                genres_set.add(g)
    
    return sorted(list(genres_set))


def filter_reviews_no_spoilers(df):
    """Remove reviews containing spoiler markers."""
    return df[
        ~(
            df['review_text'].str.contains(r'\(view spoiler\)\[', case=False, na=False) |
            df['review_text'].str.contains('spoiler alert', case=False, na=False)
        )
    ]


def filter_profanity(text):
    """Replace profane words with asterisks of equal length."""
    if not isinstance(text, str):
        return ""

    profane_words = [
        "fuck", "shit", "ass", "bitch", "crap", "damn", "hell", "bastard"

    ]

    # Create pattern with word boundaries to match whole words only
    pattern = re.compile(r'\b(' + '|'.join(profane_words) + r')\b', re.IGNORECASE)
    
    # Replace each matched word with asterisks of the same length
    return pattern.sub(lambda match: '*' * len(match.group()), text)


def display_review(review):
    """Display a single review with proper formatting."""
    # Filter profanity before displaying
    if pd.isna(review['review_text']):
        clean_text = "No review text available."
    else:
        clean_text = filter_profanity(review['review_text'])

    # Display review text with proper truncation
    review_display = clean_text[:400].replace('\n', ' ')
    if len(str(clean_text)) > 400:
        review_display += "..."
    
    st.markdown(f"> *{review_display}*")

    # Handle helpful votes display
    n_votes = review.get('n_votes', None)
    if pd.isna(n_votes) or not n_votes or int(n_votes) == 0:
        st.caption(f"⭐ **{review['rating']}/5**")
    else:
        st.caption(f"⭐ **{review['rating']}/5** | 👍 {int(n_votes)} helpful votes")


def display_similar_books(row, works_df):
    """Display similar books in an expandable section."""
    similar_ids = str(row.get('similar_books', '')).split(',')
    similar_ids = [s.strip() for s in similar_ids if s.strip().isdigit()]
    
    if similar_ids:
        similar_books_df = works_df[works_df['work_id'].astype(str).isin(similar_ids)]
        if not similar_books_df.empty:
            with st.expander("📖 Show similar books"):
                for _, sim_row in similar_books_df.head(5).iterrows():
                    year_text = int(sim_row['original_publication_year']) if pd.notna(sim_row['original_publication_year']) else 'N/A'
                    st.markdown(f"• **{sim_row['original_title']}** by *{sim_row['author']}* ({year_text})")


def safe_get_min_max(series, default_min, default_max):
    """Safely get min and max values from a series."""
    try:
        return int(series.dropna().min()), int(series.dropna().max())
    except:
        return default_min, default_max

def is_streamlit_cloud():
    """Detect if running on Streamlit Cloud."""
    return os.environ.get("STREAMLIT_SERVER_HEADLESS") == "1"

# ===============================================================================
# APP HEADER
# ===============================================================================

st.markdown("""
# 📚 BookVoyage: Your Personal Reading Discovery

### *A custom book recommendation engine built with Goodreads data*

---
""")

# Display some quick stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📖 Total Books", f"{len(works_df):,}")
with col2:
    # Show reviews count only if loaded
    if st.session_state.reviews_df is not None:
        st.metric("📝 Total Reviews", f"{len(st.session_state.reviews_df):,}")
    else:
        st.metric("📝 Reviews", "Load below ⬇️")
with col3:
    avg_rating = works_df['avg_rating'].mean()
    st.metric("⭐ Avg Rating", f"{avg_rating:.2f}")
with col4:
    unique_authors = works_df['author'].nunique()
    st.metric("✍️ Authors", f"{unique_authors:,}")

# Reviews loading section
st.markdown("### 📝 **Reviews Data**")
st.info(
    "⚠️ **Note:** This app uses a random sample of 5,000 reviews for speed and reliability. "
    "The full dataset has over 1 million reviews, but loading it requires a powerful computer and technical steps. "
    "If you're not sure how to do this, just use the app as-is—it's designed for everyone to enjoy book recommendations without any setup! "
    "\n\n"
    "💡 **Advanced users:** To use the full dataset, download `goodreads_reviews.csv` and run this app locally with enough memory. "
    "See the project README for instructions."
)

# Sidebar toggle for advanced users
st.sidebar.markdown("---")
cloud_env = is_streamlit_cloud()
if cloud_env:
    st.sidebar.warning("⚠️ Full reviews dataset is disabled on Streamlit Cloud due to memory limits.")
use_full_reviews = st.sidebar.checkbox(
    "⚠️ Use full reviews dataset (advanced, local only!)",
    value=False,
    help="Loads all 1M+ reviews. Only use if running locally with >4GB RAM. May crash Streamlit Cloud!",
    disabled=cloud_env
)

if st.session_state.reviews_df is None:
    st.info("📋 **Reviews not loaded yet.** Click below to load review data for enhanced recommendations!")
    if st.button("📥 **Load Reviews Data**", type="primary"):
        if use_full_reviews and cloud_env:
            st.error("❌ Loading the full dataset is disabled on Streamlit Cloud. Please run locally for this feature.")
        else:
            with st.spinner("📥 Loading reviews data... This may take a moment..."):
                st.session_state.reviews_df = load_reviews_data(use_full=use_full_reviews)
                if st.session_state.reviews_df is not None:
                    st.success("✅ Reviews loaded successfully!")
                    st.rerun()
else:
    st.success(f"✅ Reviews loaded! ({len(st.session_state.reviews_df):,} reviews available)")
    if st.button("🗑️ Clear Reviews Data"):
        st.session_state.reviews_df = None
        st.rerun()

st.markdown("---")

# ===============================================================================
# SIDEBAR: USER PREFERENCES
# ===============================================================================

st.sidebar.markdown("# 🎯 Customize Your Reading List")
st.sidebar.markdown("---")

# Genre and Author Selection
st.sidebar.markdown("### 📚 **Content Preferences**")

all_genres = extract_all_genres(works_df)
selected_genres = st.sidebar.multiselect(
    "🏷️ Select preferred genres:",
    all_genres,
    help="Choose one or more genres you enjoy reading"
)

all_authors = sorted(works_df['author'].dropna().unique())
selected_authors = st.sidebar.multiselect(
    "✍️ Favorite authors (optional):",
    all_authors,
    help="Select specific authors you want to see recommendations from"
)

st.sidebar.markdown("---")

# Ratings and Search Controls
st.sidebar.markdown("### ⭐ **Quality & Search**")

min_rating = st.sidebar.slider(
    "Minimum average rating:",
    min_value=1.0,
    max_value=5.0,
    value=3.5,
    step=0.1,
    help="Only show books with ratings above this threshold"
)

num_books = st.sidebar.slider(
    "Number of recommendations:",
    min_value=1,
    max_value=20,
    value=10,  # Changed from 5 to 10
    help="How many book recommendations to display"
)

search_title = st.sidebar.text_input(
    "🔍 Search for a book title (optional):",
    help="Enter keywords to search within book titles"
)

st.sidebar.markdown("---")

# Review Controls
st.sidebar.markdown("### 📝 **Review Settings**")

exclude_spoilers = st.sidebar.checkbox(
    "🚫 Exclude reviews with spoilers",
    value=True,
    help="Hide reviews that contain spoiler alerts"
)

filter_prof = st.sidebar.checkbox(
    "🔒 Filter profanity in reviews",
    value=True,
    help="Replace inappropriate language with asterisks"
)

surprise = st.sidebar.button(
    "🎲 Surprise Me!",
    help="Get random recommendations from your filtered results"
)

st.sidebar.markdown("---")

# Publication Year Filters
st.sidebar.markdown("### 📅 **Publication Era**")

# Ignore nulls and negative years for the slider minimum
all_years = works_df['original_publication_year'].dropna().astype(int)
positive_years = all_years[all_years > 0]
if not positive_years.empty:
    min_year_slider = int(positive_years.min())
else:
    min_year_slider = 1000  # fallback if no positive years
max_year = int(all_years.max())

col1, col2, col3 = st.sidebar.columns(3)
era_selected = False
year_range = (min_year_slider, max_year)

if col1.button("🏛️ Ancient\n(pre-500)"):
    # Use the actual minimum (could be negative) for ancient
    year_range = (int(all_years.min()), 500)
    era_selected = True
elif col2.button("📜 Classical\n(500-1500)"):
    year_range = (500, 1500)
    era_selected = True
elif col3.button("🌟 Modern\n(1500+)"):
    year_range = (1500, max_year)
    era_selected = True

col4, col5, col6 = st.sidebar.columns(3)
if col4.button("🎩 19th Century"):
    year_range = (1800, 1899)
    era_selected = True
elif col5.button("📺 20th Century"):
    year_range = (1900, 1999)
    era_selected = True
elif col6.button("💻 21st Century"):
    year_range = (2000, max_year)
    era_selected = True

if not era_selected:
    st.sidebar.markdown("**Custom year range:**")
    year_range = st.sidebar.slider(
        "Select range:",
        min_value=min_year_slider,
        max_value=max_year,
        value=(min_year_slider, max_year)
    )

st.sidebar.markdown("---")

# Page Count Filters
st.sidebar.markdown("### 📄 **Book Length**")

min_pages, max_pages = safe_get_min_max(works_df['num_pages'], 1, 2000)

col7, col8 = st.sidebar.columns(2)
page_selected = False
page_range = (min_pages, max_pages)

if col7.button("📖 Short\n(<250 pages)"):
    page_range = (min_pages, 250)
    page_selected = True
elif col8.button("📚 Long\n(400+ pages)"):
    page_range = (400, max_pages)
    page_selected = True

if not page_selected:
    page_range = st.sidebar.slider(
        "Page count range:",
        min_value=min_pages,
        max_value=max_pages,
        value=(min_pages, max_pages)
    )

st.sidebar.markdown("---")

# Advanced Filters
with st.sidebar.expander("🔧 **Advanced Filters**"):
    min_ratings = st.number_input(
        "Minimum number of ratings:",
        min_value=0,
        value=100,
        help="Only show books with at least this many ratings"
    )
    
    include_keyword = st.text_input(
        "Include keyword (title/description):",
        help="Books must contain this word in title or description"
    )
    
    exclude_keyword = st.text_input(
        "Exclude keyword (title/description):",
        help="Books must NOT contain this word in title or description"
    )
    
    only_with_reviews = st.checkbox(
        "Only show books with text reviews",
        value=False,
        help="Exclude books that don't have written reviews"
    )

# ===============================================================================
# FILTER BOOKS BASED ON USER INPUT
# ===============================================================================

filtered = works_df.copy()

try:
    with st.spinner("🔍 Filtering books based on your preferences..."):
        # Apply all filters
        if selected_genres:
            filtered = filtered[filtered['genres'].fillna('').apply(
                lambda x: any(g in x for g in selected_genres)
            )]
        
        if selected_authors:
            filtered = filtered[filtered['author'].isin(selected_authors)]
        
        if search_title:
            filtered = filtered[filtered['original_title'].str.contains(
                search_title, case=False, na=False
            )]

        filtered = filtered[filtered['avg_rating'] >= min_rating]

        # Publication year filter
        # Only include books with unknown years if the user selects the full range
        if year_range == (min_year_slider, max_year):
            filtered = filtered[
                ((filtered['original_publication_year'] >= year_range[0]) &
                 (filtered['original_publication_year'] <= year_range[1])) |
                (pd.isna(filtered['original_publication_year'])) |
                (filtered['original_publication_year'] < min_year_slider)  # include BCE if full range
            ]
        else:
            filtered = filtered[
                (filtered['original_publication_year'] >= year_range[0]) &
                (filtered['original_publication_year'] <= year_range[1])
            ]

        # Page count filter
        filtered = filtered[
            ((filtered['num_pages'] >= page_range[0]) &
             (filtered['num_pages'] <= page_range[1])) |
            (pd.isna(filtered['num_pages']))
        ]

        filtered = filtered[filtered['ratings_count'] >= min_ratings]

        if include_keyword:
            filtered = filtered[
                filtered['original_title'].str.contains(include_keyword, case=False, na=False) |
                filtered['description'].str.contains(include_keyword, case=False, na=False)
            ]
        
        if exclude_keyword:
            filtered = filtered[
                ~filtered['original_title'].str.contains(exclude_keyword, case=False, na=False) &
                ~filtered['description'].str.contains(exclude_keyword, case=False, na=False)
            ]
        
        if only_with_reviews:
            filtered = filtered[filtered['text_reviews_count'] > 0]

        # Sort by rating and popularity
        filtered = filtered.sort_values(
            by=['avg_rating', 'ratings_count'],
            ascending=[False, False]
        )

        # Apply surprise mode
        if surprise and not filtered.empty:
            filtered = filtered.sample(min(num_books, len(filtered)))

except Exception as e:
    st.error(f"❌ Error filtering books: {e}")
    st.stop()

# ===============================================================================
# DISPLAY RECOMMENDATIONS
# ===============================================================================

st.markdown(f"## 🎯 **Recommended Books For You**")

if filtered.empty:
    st.info("🔍 **No books found matching your preferences.** Try adjusting your filters to discover more books!")
else:
    st.success(f"📚 **Found {len(filtered)} books matching your criteria!** Showing top {min(num_books, len(filtered))} recommendations.")
    
    st.markdown("---")
    
    reading_list = []
    
    for idx, row in filtered.head(num_books).iterrows():
        # Book header with better styling
        st.markdown(f"""
        ### 📖 **{row['original_title']}**
        #### *by {row['author']}*
        """)
        
        # Book details in columns
        cols = st.columns([1, 3])
        
        with cols[0]:
            # Book cover
            if pd.notna(row['image_url']):
                st.image(row['image_url'], width=120, caption="Book Cover")
            else:
                st.image("https://via.placeholder.com/120x180?text=No+Cover", width=120)
        
        with cols[1]:
            # Book metadata
            st.markdown(f"**🏷️ Genres:** {row['genres']}")
            
            rating_display = row['avg_rating']
            rating_count = int(row['ratings_count']) if pd.notna(row['ratings_count']) else 0
            st.markdown(f"**⭐ Rating:** {rating_display}/5.0 ({rating_count:,} ratings)")
            
            year_display = int(row['original_publication_year']) if pd.notna(row['original_publication_year']) else 'Unknown'
            st.markdown(f"**📅 Published:** {year_display}")
            
            pages_display = int(row['num_pages']) if pd.notna(row['num_pages']) else 'Unknown'
            st.markdown(f"**📄 Pages:** {pages_display}")
            
            # Description with better formatting
            if pd.notna(row['description']):
                desc = row['description'][:300]
                if len(row['description']) > 300:
                    desc += "..."
                st.markdown(f"**📝 Description:** {desc}")
            else:
                st.markdown("**📝 Description:** *No description available*")

        # Reviews section - only if reviews are loaded
        if st.session_state.reviews_df is not None:
            st.markdown("#### 💬 **Reader Reviews**")

            book_reviews = st.session_state.reviews_df[st.session_state.reviews_df['work_id'] == row['work_id']]

            if exclude_spoilers:
                book_reviews = filter_reviews_no_spoilers(book_reviews)

            if book_reviews.empty:
                st.info("📝 *No reviews available for this book.*")
            else:
                review_count = min(2, len(book_reviews))
                st.markdown(f"*Showing {review_count} of {len(book_reviews)} reviews:*")

                for _, review in book_reviews.sample(review_count).iterrows():
                    if filter_prof:
                        clean_review = review.copy()
                        clean_review['review_text'] = filter_profanity(review['review_text'])
                        display_review(clean_review)
                    else:
                        display_review(review)
        else:
            st.info("📝 *Load reviews data above to see reader reviews for this book.*")

        # Similar books
        display_similar_books(row, works_df)

        # Add to reading list
        reading_list.append({
            "Title": row['original_title'],
            "Author": row['author'],
            "Genres": row['genres'],
            "Avg Rating": row['avg_rating'],
            "Year": row['original_publication_year'],
            "Pages": row['num_pages'],
            "Description": row['description'][:300] if pd.notna(row['description']) else 'No description available'
        })

        st.markdown("---")

    # Download section
    if reading_list:
        st.markdown("### 💾 **Save Your Reading List**")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            reading_df = pd.DataFrame(reading_list)
            st.download_button(
                label="📥 Download as CSV",
                data=reading_df.to_csv(index=False),
                file_name="my_summer_reading_list.csv",
                mime="text/csv",
                help="Download your curated book list to read later or share with friends!"
            )
        
        with col2:
            st.markdown("📚 **Save your curated book list to read later or share with friends!**")
            st.markdown("*Your personalized reading recommendations, ready to take anywhere.*")

# ===============================================================================
# FOOTER
# ===============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #8B5C2A; font-style: italic;'>
    📚 Created for the Maven Bookshelf Challenge 2025 | Data from Goodreads<br>
    <small>Discover your next favourite book with BookVoyage</small><br>
    <small>Created by <a href="https://github.com/EmilioMonteLuna" target="_blank">GitHub</a> |
    <a href="https://www.linkedin.com/in/emilio-montelongo-luna/" target="_blank">LinkedIn</a></small>
</div>
""", unsafe_allow_html=True)
