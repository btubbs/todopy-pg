.PHONY: db clean_files clean migrate dev js

# Both Python and Node programs will be put here.
BIN=$(shell dirname `which python`)

STATIC_DIR=todos/static
JSX_DIR=$(STATIC_DIR)/jsx
# Our React components have dependencies on each other.  This ordering is important.
JSX_MODULES=todoItem footer app
JSX_TARGETS=$(foreach module,$(JSX_MODULES),$(JSX_DIR)/$(module).js)

db:
	-psql -U postgres -c "drop database todos"
	psql -U postgres -c "create database todos"

clean_files:
	-rm -rf $(STATIC_DIR)/jsx/.module-cache
	-rm $(STATIC_DIR)/jsx/*js
	-rm -rf $(STATIC_DIR)/bower
	-rm -rf $(STATIC_DIR)/js/compiled.js
	-rm -rf $(JSX_TARGETS)

clean: db clean_files

# By letting 'nodeenv' install node.js, it will be placed into the Python virtualenv.
$(BIN)/npm:
	pip install nodeenv
	nodeenv --prebuilt -p

$(BIN)/jsx: $(BIN)/npm
	npm install -g react-tools
	touch $(BIN)/jsx # Make 'make' realize this is new.

$(BIN)/bower: $(BIN)/npm
	npm install -g bower
	touch $(BIN)/bower

$(BIN)/uglifyjs: $(BIN)/npm
	npm install -g uglify-js
	touch $(BIN)/uglifyjs

# This is slightly hacky.  $(STATIC_DIR)/bower is a folder, not a file, so Make
# is never going to recognize it as already existing.
$(STATIC_DIR)/bower: $(BIN)/bower
	cd $(STATIC_DIR); bower install --config.interactive=0

$(BIN)/todos:
	pip install -e .

migrate: $(BIN)/todos db
	todos migrate

dev: clean $(STATIC_DIR)/bower migrate

$(JSX_DIR)/%.js: $(BIN)/jsx
	jsx $(shell echo $@ | sed s/js$$/jsx/) > $@

$(STATIC_DIR)/js/compiled.js: $(BIN)/uglifyjs $(JSX_TARGETS)
	uglifyjs $(STATIC_DIR)/js/todoModel.js $(STATIC_DIR)/js/utils.js $(JSX_TARGETS) -c -m > $@

# shorthand
js: $(STATIC_DIR)/js/compiled.js
