# Build the paper

The document uses standard LaTeX packages: fontenc, lmodern, amsmath, amssymb, amsthm, geometry, booktabs and hyperref. Its bibliography is included directly.

From this directory:

~~~sh
tectonic main.tex
~~~

Alternatively, run pdflatex with halt-on-error and nonstopmode twice. The generated main.pdf corresponds to paper.pdf at the repository root.

To regenerate the complete ternary class counts from the repository root, a C++17 compiler is optional:

~~~sh
g++ -std=c++17 -O3 proof_artifacts/enumerate_partitions.cpp -o enumerate_partitions
./enumerate_partitions 10 proof_artifacts
~~~

The Python verification commands in the root README use only the standard library.
