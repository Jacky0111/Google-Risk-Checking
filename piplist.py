from pip._internal.operations import freeze

for package in freeze.freeze():
    print(package)
