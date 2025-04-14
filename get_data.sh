# Export the environment variables
source .env

# Make temporary directory for data download
mkdir -p data/images/raw

# Download the data
kaggle competitions download dogs-vs-cats -p data/images/raw
