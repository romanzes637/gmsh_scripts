<img alt="Readme" src="/images/readme.jpg" width="800" height="800">

# gmsh_scripts
3D structured/unstructured/tetrahedral/hexahedral multi-block mesh generator 
with boolean operations based on [gmsh](https://gmsh.info/)

## Documentation
* [English](https://gmsh-scripts.readthedocs.io/en/latest/)
* [Français](https://gmsh-scripts.readthedocs.io/fr/latest/)
* [Русский](https://gmsh-scripts.readthedocs.io/ru/latest/)

## Installation
### Pip
1. [Download](https://www.python.org/downloads/) and install Python
2. Install gmsh_scripts
```shell
pip install gmsh-scripts
```
3. Create or [download](https://github.com/romanzes637/gmsh_scripts/blob/master/examples/matrix/matrix.json) input file
```json
{
  "metadata": {
    "run": {
      "factory": "occ"
    }
  },
  "data": {
    "class": "block.Matrix",
    "matrix": [
      [-1, 0, 1],
      [-2, 0, 2],
      [-3, 0, 3]
    ]
  }
}
```
4. Create mesh
```shell
python -m gmsh_scripts matrix.json
```

### Github
1. [Download](https://www.python.org/downloads/) and install Python
2. [Download](https://github.com/romanzes637/gmsh_scripts) gmsh_scripts
3. Install requirements
```shell
pip install -r requirements/prod.txt
```
4. Create or [download](https://github.com/romanzes637/gmsh_scripts/blob/master/examples/matrix/matrix.json) input file
5. Create mesh
```shell
python gmsh_scripts/run.py matrix.json
```

### Result
<img alt="Matrix" src="/images/matrix.png" width="200" height="200">

## Complex [mesh](https://downgit.github.io/#/home?url=https://github.com/romanzes637/gmsh_scripts/tree/master/examples/experiment/sweden) from examples
### Create mesh
```shell
python -m gmsh_scripts all_heater_plug.json
```
<img alt="Experiment" src="/images/sweden_experiment.png" width="400" height="400">

### Plot tree
```shell
pin install gmsh_scripts[viz]
```
```shell
python -m gmsh_scripts all_heater_plug.json --plot
```
<img alt="Experiment tree" src="/images/sweden_experiment_tree.png" width="400" height="400">

## [Examples](https://downgit.github.io/#/home?url=https://github.com/romanzes637/gmsh_scripts/tree/master/examples) Click them!

<a href="https://github.com/romanzes637/gmsh_scripts/blob/master/examples/cylinder/simple.json">
<img alt="Multilayerd Cylinder" src="/images/simple_cylinder.png" width="200" height="200">
</a>
<a href="https://github.com/romanzes637/gmsh_scripts/blob/master/examples/torus/simple.yaml">
<img alt="Simple Torus" src="/images/simple_torus.png" width="200" height="200">
</a>
<a href="https://github.com/romanzes637/gmsh_scripts/blob/master/examples/torus/simple_tokamak.yaml">
<img alt="Simple Tokamak" src="/images/simple_tokamak.png" width="200" height="200">
</a>
<a href="https://github.com/romanzes637/gmsh_scripts/blob/master/examples/torus/simple_stellarator.yaml">
<img alt="Simple Stellarator" src="/images/simple_stellarator.png" width="200" height="200">
</a>
<a href="https://github.com/romanzes637/gmsh_scripts/blob/master/examples/well_boundary/wells_parent.json">
<img alt="Wells" src="https://github.com/romanzes637/gmsh_scripts/blob/master/images/wells_parent.png" width="200" height="200">
</a>
<a href="https://github.com/romanzes637/gmsh_scripts/tree/master/examples/matrix/cross_section_1">
<img alt="Cross section 1" src="https://github.com/romanzes637/gmsh_scripts/blob/master/images/cross_section_1.png" width="200" height="200">
</a>
<a href="https://github.com/romanzes637/gmsh_scripts/tree/master/examples/matrix/cross_section_2">
<img alt="Cross section 2" src="https://github.com/romanzes637/gmsh_scripts/blob/master/images/cross_section_2.png" width="200" height="200">
</a>
<a href="https://github.com/romanzes637/gmsh_scripts/tree/master/examples/cylinder/core.yaml">
<img alt="Core" src="https://github.com/romanzes637/gmsh_scripts/blob/master/images/core.png" width="200" height="200">
</a>
<a href="https://github.com/romanzes637/gmsh_scripts/tree/master/examples/quarter_layer/simple.yaml">
<img alt="Quarter layer" src="https://github.com/romanzes637/gmsh_scripts/blob/master/images/simple_quarter_layer.png" width="200" height="200">
</a>
<a href="https://github.com/romanzes637/gmsh_scripts/tree/master/examples/quarter_layer_with_holes/main.yaml">
<img alt="Quarter layer with holes" src="https://github.com/romanzes637/gmsh_scripts/blob/master/images/quarter_layer_with_holes.png" width="200" height="200">
</a>
<a href="https://github.com/romanzes637/gmsh_scripts/tree/master/examples/matrix/large_matrix.yaml">
<img alt="Large Matrix" src="https://github.com/romanzes637/gmsh_scripts/blob/master/images/large_matrix.png" width="200" height="200">
</a>
<a href="https://github.com/romanzes637/gmsh_scripts/tree/master/examples/block/custom_block.yaml">
<img alt="Custom Block" src="https://github.com/romanzes637/gmsh_scripts/blob/master/images/custom_block.png" width="200" height="200">
</a>
<a href="https://github.com/romanzes637/gmsh_scripts/tree/master/examples/half_layer/simple.yaml">
<img alt="Half layer" src="https://github.com/romanzes637/gmsh_scripts/blob/master/images/simple_half_layer.png" width="200" height="200">
</a>
<a href="https://github.com/romanzes637/gmsh_scripts/tree/master/examples/half_layer_with_holes/main.yaml">
<img alt="Half layer with holes" src="https://github.com/romanzes637/gmsh_scripts/blob/master/images/half_layer_with_holes.png" width="200" height="200">
</a>

## [Examples album](https://photos.app.goo.gl/KngvSr6ttbyIdFEX2)

## [Video tutorials (In Russian)](https://youtube.com/playlist?list=PLNPHDKBRjaZmMzjxtoZVzeWSHZB-x9ayi)

## Cite

### gmsh
[Geuzaine and J.-F. Remacle. Gmsh: a three-dimensional finite element mesh generator with built-in pre- and post-processing facilities. International Journal for Numerical Methods in Engineering 79(11), pp. 1309-1331, 2009](https://gmsh.info/doc/preprints/gmsh_paper_preprint.pdf)

### gmsh scripts
[Butov R.A., Drobyishevsky N.I., Moiseenko E.V., Tokarev Yu. N. Mesh generation for radioactive waste management tasks. Radioactive Waste, 2021, no. 1 (14), pp. 87—95. DOI: 10.25283/2587-9707-2021-1-87-95. (In Russian)](http://eng.radwaste-journal.ru/docs/journals/27/mesh_generation_for_radioactive_waste_management_tasks.pdf)

## Contacts
Roman Pashkovsky

https://github.com/romanzes637

romapasky@gmail.com

Made in [Nuclear Safety Institute of the Russian Academy of Sciences](http://en.ibrae.ac.ru/) (IBRAE RAN)
