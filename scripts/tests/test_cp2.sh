mkdir -p cp_test/sparse/1
touch cp_test/sparse/1/images.bin
cp_test_dir="cp_test/sparse"
SPARSE_DIR="$cp_test_dir/0"
rm -rf "$SPARSE_DIR"
BEST_MODEL="$cp_test_dir/1/"
cp -r "$BEST_MODEL" "$SPARSE_DIR"
ls -la cp_test/sparse/0
