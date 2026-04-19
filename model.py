import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset
df = pd.read_csv('cleaned_data3.csv')

# Clean data
df = df.dropna(subset=['name', 'category', 'description'])
df = df.reset_index(drop=True)

# Normalize text
df['name'] = df['name'].astype(str)
df['category'] = df['category'].astype(str).str.lower()
df['description'] = df['description'].astype(str)

# Combine features
df['features'] = df['category'] + " " + df['description']

# Vectorization
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df['features'])

# Similarity matrix
similarity = cosine_similarity(tfidf_matrix)

# 🔥 Safe image function (VERY IMPORTANT)
def get_image(url):
    url = str(url).split(',')[0].strip()   # get first image

    # if valid URL → use it
    if url.startswith("http"):
        return url

    # else fallback
    return "https://via.placeholder.com/150"


# 🎯 Recommendation
def recommend(product_name):
    product_name = product_name.lower()

    if product_name not in df['name'].str.lower().values:
        return []

    idx = df[df['name'].str.lower() == product_name].index[0]

    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    recommended = []

    for i in scores[1:5]:
        product = df.iloc[i[0]]

        recommended.append({
            "name": product['name'],
            "price": product.get('price', 'N/A'),
            "image": get_image(product['image'])
        })

    return recommended


# 🎯 Category-wise products
def get_by_category(category_name):
    category_name = category_name.lower()

    filtered = df[df['category'] == category_name]

    products = []

    for _, row in filtered.iterrows():
        products.append({
            "name": row['name'],
            "price": row.get('price', 'N/A'),
            "image": get_image(row['image'])
        })

    return products


# 🎯 Get all categories
def get_categories():
    return sorted(df['category'].dropna().unique())


# 🔍 Simple search
def search_products(query):
    results = df[df['name'].str.contains(query, case=False, na=False)]

    products = []

    for _, row in results.head(20).iterrows():
        products.append({
            "name": row['name'],
            "price": row.get('price', 'N/A'),
            "image": get_image(row['image'])
        })

    return products