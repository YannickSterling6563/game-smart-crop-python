from smart_crop_service import InfraiClient, crop_asset, demo_request


if __name__ == "__main__":
    print(crop_asset(demo_request(), InfraiClient()))
