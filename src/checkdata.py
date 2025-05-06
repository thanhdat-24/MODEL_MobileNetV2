import os

# Đường dẫn dataset
dataset_path = "dataset_vietnamese"
train_path = os.path.join(dataset_path, "Training")
test_path = os.path.join(dataset_path, "Test")

# Lấy danh sách class
train_classes = set(os.listdir(train_path))
test_classes = set(os.listdir(test_path))

# So sánh tên class
if train_classes == test_classes:
    print("✅ Tên các class đã đồng bộ giữa Training và Test.")
else:
    print("❌ Tên các class KHÔNG đồng bộ.")
    only_in_train = train_classes - test_classes
    only_in_test = test_classes - train_classes

    if only_in_train:
        print("\n📁 Các class chỉ có trong Training:")
        for cls in sorted(only_in_train):
            print(f"- {cls}")
    if only_in_test:
        print("\n📁 Các class chỉ có trong Test:")
        for cls in sorted(only_in_test):
            print(f"- {cls}")
