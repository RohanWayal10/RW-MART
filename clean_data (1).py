import pandas as pd
import os

# ── Load ──────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, 'Combined_dataset.csv'))

print("Original shape :", df.shape)
print("Columns        :", df.columns.tolist())

# ── Rename columns ────────────────────────────────────────────────
df = df.rename(columns={
    'title':               'name',
    'product_description': 'description',
    'images':              'image',          # will keep only first image
})

# ── Drop rows missing critical fields ─────────────────────────────
df = df.dropna(subset=['name', 'category', 'description', 'image'])

# ── Strip whitespace ──────────────────────────────────────────────
df['name']        = df['name'].str.strip()
df['category']    = df['category'].str.strip().str.lower()
df['description'] = df['description'].str.strip()

# ── Keep ONLY the first image URL ─────────────────────────────────
#    The images column contains comma-separated URLs; take the first one
df['image'] = (
    df['image']
    .astype(str)
    .str.split(',')
    .str[0]
    .str.strip()
)

# ── Clean price → numeric ─────────────────────────────────────────
df['price'] = (
    df['final_price']
    .astype(str)
    .str.replace(r'[₹",\s]', '', regex=True)
)
df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0).astype(int)

# ── Clean rating → numeric ────────────────────────────────────────
df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)

# ── Remove duplicates ─────────────────────────────────────────────
df = df.drop_duplicates(subset=['name'])

# ── Select & order final columns ─────────────────────────────────
df = df[[
    'product_id',
    'name',
    'category',
    'description',
    'price',
    'rating',
    'ratings_count',
    'discount',
    'image',          # ← single image URL only
]].reset_index(drop=True)

# ── Save ──────────────────────────────────────────────────────────
out_path = os.path.join(BASE_DIR, 'cleaned_data.csv')
df.to_csv(out_path, index=False)

print(f"\n✅ Cleaned data saved → {out_path}")
print(f"   Rows  : {len(df)}")
print(f"   Cols  : {df.columns.tolist()}")
print(f"\nSample images (first 5):")
print(df['image'].head(5).to_string())
print(f"\nSample rows:")
print(df[['name','category','price','rating','image']].head(5).to_string())
print(df.shape)