SCONS_CMD = scons -Q

.PHONY = test mocks

%:
	$(SCONS_CMD) -j4 $@

clean:
	$(SCONS_CMD) -c