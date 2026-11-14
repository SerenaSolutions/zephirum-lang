# SPDX-License-Identifier: Apache-2.0
CXX ?= g++
CXXFLAGS := -O2 -Wall -Wextra -std=c++17 -fPIC
all: libzyql.so
libzyql.so: zyql_verdict.cpp zyql_verdict.hpp
	$(CXX) $(CXXFLAGS) -shared -o $@ zyql_verdict.cpp
clean:
	rm -f libzyql.so
.PHONY: all clean
