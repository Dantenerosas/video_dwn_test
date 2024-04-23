from minio import Minio
from minio.error import S3Error


def main():
    client = Minio(
        "*",
        access_key="*",
        secret_key="*",
        secure=True
    )

    found = client.bucket_exists("clean-internet-oculus-integration-dev")
    if not found:
        client.make_bucket("clean-internet-oculus-integration-dev")
    else:
        print("Bucket 'clean-internet-oculus-integration-dev' already exists")

    client.fput_object(
        "clean-internet-oculus-integration-dev", "4uv2GNc_ybc_1080p.mp4", "/Users/garickbadalov/PycharmProjects/video_downloader_service/downloads/Youtube/4uv2GNc_ybc_1080p.mp4",
    )
    print(
        "'/Users/garickbadalov/PycharmProjects/video_downloader_service/downloads/Youtube/4uv2GNc_ybc_1080p.mp4' is successfully uploaded as "
        "object '4uv2GNc_ybc_1080p.mp4' to bucket 'clean-internet-oculus-integration-dev'."
    )


if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        print("error occurred.", exc)