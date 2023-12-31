import pandas as pd
import requests
from io import StringIO, BytesIO
from PIL import Image
import os
import sys


# specify location of csv of species to download
if len(sys.argv) > 1:
    csvpath = sys.argv[1]
else:
    csvpath = input("Please enter path to csv file with selected bird species for image retrieval\n(format: index,species_no,scientific_name)")

# load species to download
selected_birds_df = pd.read_csv(csvpath)

# # Import tracking_df
# tracking_csv_path = "../bird_data/tracking.csv"  # Update with the actual path
# if os.path.exists(tracking_csv_path):
#     tracking_df = pd.read_csv(tracking_csv_path)
# else:
#     # If the tracking file doesn't exist, create a new DataFrame
#     tracking_df = pd.DataFrame(columns=['species_no', 'downloaded', 'downloaded_no'])

# import bird_master_df
#bird_master_df = pd.read_csv('../bird_data/test_script.csv')
bird_master_df = pd.read_csv('../bird_data/bird_master_df.csv') # csv source should be put in the cloud later
bird_master_df = bird_master_df.drop(columns='Unnamed: 0') # drop weird column

species_no_to_download = selected_birds_df['species_no'].tolist()

def image_retrieval(bird_master_df, selected_birds_df, mydir=None, size = (256, 256), number = 1):
    '''Download images based on master url file (~10Mio. entries for ~11,000 species) for selected species'''

    # Temporary merged data frame based on a filtered version of bird_master_df
    temp_df = bird_master_df[bird_master_df['species_no'] == selected_birds_df['species_no'].iloc[0]]

    temp_df_row_count = temp_df.shape[0]

    temp_list = []

    print(f"temp_df created with {temp_df_row_count} rows")

    itercount = 0

    # Iterate over rows in temp_df
    for index, row in temp_df.iterrows():

        itercount += 1

        print(f"Now working on row {itercount} / {temp_df_row_count} in temp_df. There are {temp_df_row_count - (itercount)} rows left.")

        if row['image_id'] in temp_list:
            print("Already successfully downloaded a picture from this list of duplicate urls")
            continue

        # Locate download links
        url_im = row['image_url']

        ## Attempt download via link ('image_url') from temp_df
        try:
            response = requests.get(url_im, timeout=5)
            response.raise_for_status()  # Raise an HTTPError for bad responses
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image from {url_im}: {e}")
            continue  # Skip to the next iteration

        # Check if the download was successful
        if response.status_code == 200:

            try:
                im = Image.open(BytesIO(response.content))

                # Resize image using im.thumbnail(size, Image.ANTIALIAS) with 256 as the maximum dimension while keeping original image proportions
                im.thumbnail(size, Image.LANCZOS)

                # Create folder if it doesn't exist
                if mydir is None:
                    mydir = os.getcwd()
                    species_folder = os.path.join(mydir, f"{row['species_no']}")
                    os.makedirs(species_folder, exist_ok=True)

                # Save resulting image via im.save as [species_no]_[xxxx].png in the corresponding folder created above
                im_dir = os.path.join(species_folder, f"{row['species_no']}_{number:04d}.png")

                # Check if the file already exists, if not, save the image
                if not os.path.exists(im_dir):
                    im.save(im_dir)

                    ## remove duplicate image_ids from temp_df


                    temp_list.append(row['image_id'])

                    # 1. retrieve image_id of successfully saved image
                    #temp_img_id = row['image_id']

                    # 2. Update temp_df and delete all rows below with matching image_id
                    # selec_birds_df.drop(0, inplace=True)
                    #temp_df = temp_df[temp_df['image_id'] != temp_img_id]

                    print(f"Saved: {im_dir}")
                else:
                    print(f"Skipped (already exists): {im_dir}")

                # Increment the numbering variable for the next image
                number += 1

            except:

                pass

    print('Iterating over the rows of temp_df has been completed.')

print(species_no_to_download)

for i in range(len(species_no_to_download)):

    print(f"No starting to working on species {i+1} / {len(species_no_to_download)}: species_no {species_no_to_download[i]}")

    print(selected_birds_df)

    function_input_df = selected_birds_df.loc[selected_birds_df['species_no'] == species_no_to_download[i]]
    print(function_input_df)

    image_retrieval(bird_master_df, function_input_df)

print(f"Finished download of {len(species_no_to_download)} specified species. Script ended.")
