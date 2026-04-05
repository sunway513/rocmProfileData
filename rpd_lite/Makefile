# rpd_lite — Self-contained GPU profiler
# Dependencies: libamdhip64, libhsa-runtime64, libsqlite3
# NO roctracer, NO rocprofiler-sdk

HIP_PATH ?= /opt/rocm
PREFIX ?= /usr/local

CXX ?= g++
CXXFLAGS = -O3 -g -fPIC -std=c++17 \
           -I$(HIP_PATH)/include \
           -I$(HIP_PATH)/include/hsa \
           -D__HIP_PLATFORM_AMD__ -DAMD_INTERNAL_BUILD

LDFLAGS = -shared -rdynamic \
          -L$(HIP_PATH)/lib \
          -lhsa-runtime64 -lsqlite3 \
          -ldl -lpthread

SRCS = rpd_lite.cpp hip_intercept.cpp roctx_shim.cpp hsa_intercept.cpp
OBJS = $(SRCS:.cpp=.o)
TARGET = librpd_lite.so

.PHONY: all clean install test

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) -o $@ $^ $(LDFLAGS)
	@echo "Built $(TARGET)"
	@echo "  Dependencies: libamdhip64, libhsa-runtime64, libsqlite3"
	@echo "  NO roctracer, NO rocprofiler-sdk"
	@ldd $@ | grep -E "roctracer|rocprofiler-sdk" && echo "ERROR: unwanted dependency found!" && exit 1 || echo "  Verified: clean dependency chain (rocprofiler-register is OK — part of HSA runtime)"

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

install: $(TARGET)
	cp $(TARGET) $(PREFIX)/lib/
	ldconfig
	@echo "Installed to $(PREFIX)/lib/$(TARGET)"

clean:
	rm -f $(OBJS) $(TARGET)

# Usage:
#   HSA_TOOLS_LIB=librpd_lite.so python my_script.py
#   sqlite3 trace.rpd "select * from top limit 20;"
test:
	@echo "=== Quick test ==="
	HSA_TOOLS_LIB=$(CURDIR)/$(TARGET) \
		python3 -c "import torch; x=torch.randn(512,512,device='cuda'); y=x@x; torch.cuda.synchronize(); print('OK')"
	@echo "=== Trace results ==="
	sqlite3 trace.rpd "select * from top limit 10;" 2>/dev/null || true
	sqlite3 trace.rpd "select count(*) as api_count from rocpd_api;" 2>/dev/null || true
	sqlite3 trace.rpd "select count(*) as kernel_count from rocpd_op;" 2>/dev/null || true
