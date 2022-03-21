![readme](/images/readme.jpg)

# gmsh_scripts
3D structured/unstructured/tetrahedral/hexahedral multi-block mesh generator 
with boolean operations based on [gmsh](https://gmsh.info/)

## Installation
### Pip
1. [Download](https://www.python.org/downloads/) and install Python
2. Install gmsh_scripts
```shell
pip install gmsh-scripts
```
3. Create or [download](matrix.json) input file
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
4. Create or [download](https://downgit.github.io/#/home?url=https://github.com/romanzes637/gmsh_scripts/blob/master/examples/matrix/matrix.json) input file
5. Create mesh
```shell
python gmsh_scripts/run.py matrix.json
```

### Result
![readme](/images/matrix.png)

## Complex [mesh](https://downgit.github.io/#/home?url=https://github.com/romanzes637/gmsh_scripts/tree/master/examples/experiment/sweden) from examples
### Create mesh
```shell
python -m gmsh_scripts all_heater_plug.json
```
![readme](/images/sweden_experiment.png)
### Plot tree
```shell
python -m gmsh_scripts all_heater_plug.json --plot
```
![readme](/images/sweden_experiment_tree.png)

## [Examples](https://downgit.github.io/#/home?url=https://github.com/romanzes637/gmsh_scripts/tree/master/examples)

## [Examples album](https://photos.app.goo.gl/KngvSr6ttbyIdFEX2)

## [User manual (In Russian)](https://docs.google.com/document/d/166MPpgo0n661rmQZg7IS_MhNxlCueseOpwgqPBXQ8hI/edit?usp=sharing)

## [Video tutorials (In Russian)](https://youtube.com/playlist?list=PLNPHDKBRjaZmMzjxtoZVzeWSHZB-x9ayi)

## Cite

### gmsh
[Geuzaine and J.-F. Remacle. Gmsh: a three-dimensional finite element mesh generator with built-in pre- and post-processing facilities. International Journal for Numerical Methods in Engineering 79(11), pp. 1309-1331, 2009](https://gmsh.info/doc/preprints/gmsh_paper_preprint.pdf)

### gmsh scripts
[Butov R.A., Drobyishevsky N.I., Moiseenko E.V., Tokarev Yu. N. Mesh generation for radioactive waste management tasks. Radioactive Waste, 2021, no. 1 (14), pp. 87—95. DOI: 10.25283/2587-9707-2021-1-87-95. (In Russian)](http://eng.radwaste-journal.ru/docs/journals/27/mesh_generation_for_radioactive_waste_management_tasks.pdf)

## Contacts
Roman Butov

https://github.com/romanzes637

romanbutov637@gmail.com

Made in [Nuclear Safety Institute of the Russian Academy of Sciences](http://en.ibrae.ac.ru/) (IBRAE RAN)
