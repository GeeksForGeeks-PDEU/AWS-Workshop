import dotenv
import os
dotenv.load_dotenv()

import streamlit as st
import boto3

def upload_image_to_s3(file, bucket_name):
    s3 = boto3.client('s3')
    try:
        s3.upload_fileobj(file, bucket_name, file.name)
        return True
    except Exception as e:
        st.error(f"Error uploading image to S3: {e}")
        return False

def fetch_bucket_names():
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    bucket_names = [bucket['Name'] for bucket in response['Buckets']]
    return bucket_names

def fetch_image_keys(bucket_name):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name)
    image_keys = [obj['Key'] for obj in response.get('Contents', [])]
    return image_keys

def fetch_image_urls(bucket_name, expiry_time_hours=1):
    session = boto3.Session(region_name=os.getenv('AWS_REGION') , aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
    s3 = session.client('s3')    
    bucket_url = f"https://{bucket_name}.s3.amazonaws.com/"
    image_keys = fetch_image_keys(bucket_name)

    # Generate presigned URLs for each image key with expiry time
    image_urls = []
    for key in image_keys:
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': key},
            ExpiresIn=expiry_time_hours * 3600  # Expiry time in seconds
        )
        image_urls.append((bucket_url + key, presigned_url))

    return image_urls
def main():
    st.title("S3 Image Browser")

    # Fetch S3 bucket names
    bucket_names = fetch_bucket_names()

    # Sidebar navigation
    page = st.sidebar.radio("Navigate", ["Upload Image", "Browse Images"])

    if page == "Upload Image":
        upload_image_page()
    elif page == "Browse Images":
        browse_images_page(bucket_names)


def upload_image_page():
    st.header("Upload Image to S3 Bucket")

    # Fetch S3 bucket names
    bucket_names = fetch_bucket_names()
    
    # Dropdown to select S3 bucket
    selected_bucket = st.selectbox("Select S3 Bucket", bucket_names)

    # File uploader for image
    uploaded_file = st.file_uploader("Choose an image to upload")

    if uploaded_file is not None:
        # Display selected image
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

        # Button to upload image to S3
        if st.button("Upload to S3"):
            if upload_image_to_s3(uploaded_file, selected_bucket):
                st.success("Image uploaded to S3 successfully!")
            else:
                st.error("Failed to upload image to S3.")

def browse_images_page(bucket_names):
    st.header("Browse Images in S3 Bucket")

    # Dropdown to select S3 bucket
    selected_bucket = st.selectbox("Select S3 Bucket", bucket_names)
    print(selected_bucket)

    # Fetch image URLs from selected S3 bucket
    image_urls = fetch_image_urls(selected_bucket)

    # Display images
    st.markdown("### Images:")
    for image_url, presigned_url in image_urls:

        print(image_url)
        print(presigned_url)
        st.image(image_url, caption=image_url, use_column_width=True)

if __name__ == "__main__":
    main()
