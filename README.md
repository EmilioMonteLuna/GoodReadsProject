# 📚 BookVoyage: Your Personal Reading Discovery

*A submission for the [Maven Bookshelf Challenge 2025](https://www.mavenanalytics.io/challenges)*  
Created by [Emilio Montelongo Luna](https://www.linkedin.com/in/emilio-montelongo-luna/)

---

## 📝 Overview

BookVoyage is an interactive web app that helps users discover their perfect summer reading list, tailored to their unique tastes, using real Goodreads data. Built for the Maven Bookshelf Challenge, it demonstrates practical data storytelling, product design, and user-focused interactivity.

---

## 📖 About the Challenge

The **Maven Bookshelf Challenge** invites participants to build a personalized book recommendation engine using real Goodreads data. The goal is to help readers discover their ideal summer reading list, tailored to their unique preferences — based on genres, authors, reviews, and more.

---

## 🚀 About BookVoyage

**BookVoyage** is an interactive web application built with **Python** and **Streamlit** that helps users:

- 🔍 Discover books by genre, author, rating, publication year, page count, and keywords  
- 💬 Explore real user reviews with spoiler and profanity filtering  
- 📖 Browse similar books  
- 📥 Download a custom reading list  
- 🎲 Use "Surprise Me!" mode for random picks based on filters  

---

## 🛠️ Features

- ✅ **Interactive Filters**: Genres, authors, ratings, publication years, page count, and more  
- ✅ **Spoiler-Free Reviews**: Option to exclude spoiler-tagged reviews and filter profanity  
- ✅ **Personalized Book List**: Tailored recommendations based on your preferences  
- ✅ **Download as CSV**: Export your reading list with one click  
- ✅ **Surprise Me Mode**: Instantly discover random suggestions  
- ✅ **Clean UI**: Built with Streamlit for accessibility and responsiveness  

---

## 💾 Data Sources

This app uses datasets provided by Maven Analytics and Goodreads:

- `goodreads_works.csv` — Metadata for thousands of books  
- `goodreads_reviews.csv` — Over 1 million user reviews (⚠️ **large file: ~1.3GB**)  
- `goodreads_data_dictionary.csv` — Data dictionary for understanding the datasets

---

## 🧑‍💻 How to Run Locally

> ⚠️ The full reviews dataset is too large for GitHub and Streamlit Cloud. You must download it separately (instructions below), or use a smaller sample version for deployment.

### 1. Clone the Repo

```bash
git clone https://github.com/EmilioMonteLuna/GoodReadsProject.git
cd GoodReadsProject
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Load the Datasets

#### Option A: Use Full Dataset (Locally)

- Create a `Data/` folder and place the following CSVs inside:

```
Data/
├── goodreads_works.csv
├── goodreads_reviews.csv  ← (must be downloaded manually)
```

You can download the full `goodreads_reviews.csv` from the [Maven Bookshelf Challenge dataset](https://maven-datasets.s3.us-east-1.amazonaws.com/Goodreads+Book+Reviews/Goodreads+Book+Reviews.zip).  
Ensure the file is named exactly `goodreads_reviews.csv`.

#### Option B: Use Sample Dataset (Recommended for Deployment)

- Use a smaller sample like `goodreads_reviews_sample.csv` to avoid memory/time issues.
- To create a sample, run:

```python
import pandas as pd
df = pd.read_csv("Data/goodreads_reviews.csv")
df.sample(5000, random_state=42).to_csv("Data/goodreads_reviews_sample.csv", index=False)
```

---

### 4. Run the App

```bash
streamlit run ReadingListProgram.py
```

Open your browser to [http://localhost:8501](http://localhost:8501)

---

## ☁️ Deploying to Streamlit Cloud

Because of size limitations, **do not include the full reviews file in your GitHub repository**. Instead:

1. Add the file to `.gitignore`:
    ```bash
    # Ignore large dataset
    Data/goodreads_reviews.csv
    ```
2. Modify your code to:
    - Check if the file exists
    - Use a smaller file like `goodreads_reviews_sample.csv` if not

3. Push and deploy using Streamlit Cloud

---

## 🔗 Useful Links

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Cloud Deployment Guide](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app)
- [GitHub Repository](https://github.com/EmilioMonteLuna/GoodReadsProject)
- [Live Streamlit App](https://bookvoyage.streamlit.app/)

---

## 📜 License

This project is for educational and portfolio use as part of the Maven Bookshelf Challenge.

---
