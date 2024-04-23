from minio import Minio
from minio.error import S3Error


def main():
    client = Minio(
        "*",
        access_key="*",
        secret_key="*",
        secure=True
    )

    # Make 'asiatrip' bucket if not exist.
    found = client.bucket_exists("clean-internet-oculus-integration-dev")
    if not found:
        client.make_bucket("clean-internet-oculus-integration-dev")
    else:
        print("Bucket 'clean-internet-oculus-integration-dev' already exists")

    # Upload '/home/user/Photos/asiaphotos.zip' as object name
    # 'asiaphotos-2015.zip' to bucket 'asiatrip'.
    file_name = '4uv2GNc_ybc_1080p.mp4'
    path = f'/home/Projects/video_downloader_service/downloads/Youtube/{file_name}'
    client.fput_object(
        "clean-internet-oculus-integration-dev", file_name, path,
    )
    print(
        f"'{path}' is successfully uploaded as "
        f"object '{file_name}' to bucket 'clean-internet-oculus-integration-dev'."
    )


if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        print("error occurred.", exc)