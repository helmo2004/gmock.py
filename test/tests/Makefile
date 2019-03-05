GTEST_BASE=../../googletest
GMOCK_DIR=$(GTEST_BASE)/googlemock
GMOCK_INC=$(GMOCK_DIR)/include
GTEST_INC=$(GTEST_BASE)/googletest/include
GMOCK_MAIN_LIB=$(GMOCK_DIR)/make/gmock_main.a

gmock_main: $(GMOCK_MAIN_LIB)

$(GMOCK_MAIN_LIB):
	make -C $(GMOCK_DIR)/make gmock_main.a

OS_CLANG_ARGS=$(shell python get_os_dependent_clang_args.py)
	
generated:
	mkdir generated
	
generated/MockA.hpp generated/MockA.cpp: generated include/A.hpp include/nested_include/B.hpp include/nested_include/C.hpp ../../gmock.py
	python ../../gmock.py include/A.hpp -d generated -- -I include/nested_include $(OS_CLANG_ARGS)
	
test: generated/MockA.hpp src/TestA.cpp $(GMOCK_MAIN_LIB)
	g++ -std=c++11 generated/MockA.cpp src/TestA.cpp -I. -I include/nested_include -I$(GMOCK_INC) -I$(GTEST_INC) -o test $(GMOCK_MAIN_LIB) -pthread 
	
run_test: test
	./test

hard-clean: clean
	make -C $(GMOCK_DIR)/make clean

clean:
	rm -rf generated
	rm -f test