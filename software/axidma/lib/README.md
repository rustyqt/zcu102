
# Cross-Compile libaxidma library
aarch64-linux-gnu-gcc -Wall -Wextra -Werror -std=gnu99 -g -O0 -fPIC -I /usr/include/python3.8 -shared -Wno-missing-field-initializers libaxidma.c -o libaxidma.so

# Dummy Native Compile libaxidma library
gcc -std=gnu99 -g -O0 -fPIC -I /usr/include/python3.8 -shared -Wno-missing-field-initializers libaxidma.c -o libaxidma.so
