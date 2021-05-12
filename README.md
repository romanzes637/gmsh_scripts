![readme](/images/readme.png)

# gmsh_scripts
Mixed (structured/unstructured) 3D mesh generator with curved cuboid elements 
(Primitives) based on gmsh https://gmsh.info/

## Installation
1. Download and install python https://www.python.org/downloads/
2. Install numpy and gmsh packages
```shell
pip install -r requirements.txt 
```
3. Download gmsh_scripts from https://github.com/romanzes637/gmsh_scripts
4. To create mesh use complex_factory.py script
```shell
python complex_factory -i [INPUT_FILE]
```

## Example
Input file test_cylinder_simple.json of complex "Cylinder" (axisymmetric multilayer geometry)
```json
{
  "metadata": {
    "type": "class_arguments",
    "class_name": "Cylinder",
    "description": "Test Cylinder simple"
  },
  "arguments": {
    "factory": "geo",
    "radii": [1, 2],
    "heights": [1, 2],
    "layers_lcs": 0.5,
    "volumes_names": ["V1", "V2"],
    "layers_volumes_names": [[0, 1], [0, 1]],
    "transfinite_r_data": [[3, 0, 1], [5, 0, 0.7]],
    "transfinite_h_data": [[3, 0, 1], [9, 1, 3.0]],
    "transfinite_phi_data": [7, 0, 1]
  }
}
```
File consists of 2 sections: `"metadata"` and `"arguments"`.
Section `"metadata"` describes type of input file `"type"`, name of a Complex 
`"class_name"` and text field `"description"`.
Section `"arguments"` contains input data for Complex "Cylinder":
* `"factory"` - gmsh kernel: “geo” (default) or  “occ” (OpenCascade)
* `"radii"` - radii of multilayer cylinder: two cylinders with 1 and 2 meters
* `"heights"` - heights of multilayer cylinder layers: two layers of 1 and 2 meters
* `"layers_lcs"` - mesh characteristic length
* `"volumes_names"` - names for mesh volumes
* `"layers_volumes_names"` - map of volumes names by layers: from bottom to top, from center to side
* `"transfinite_r_data"` - data for structured mesh by radial layers, \[number of nodes, struct type, size rate\]. Struct types: 0 - linear, 1 - centered. Size rate is a change of element sizes from center to side
* `"transfinite_h_data"` - data for structured mesh by height layers. Size rate is from bottom to top
* `"transfinite_phi_data"` - data for circumferential structured mesh

### Unstructured tetrahedral mesh
```shell
python complex_factory -i input/test_cylinder_simple.json
```
![unstruct_tetrahedral](/images/test_cylinder_simple.png)

### Structured tetrahedral mesh
```shell
python complex_factory -i input/test_cylinder_simple.json -t
```
![struct_tetrahedral](/images/test_cylinder_simple_t.png)

### Structured hexahedral mesh
```shell
python complex_factory -i input/test_cylinder_simple.json -tr
```
![struct_hexahedral](/images/test_cylinder_simple_tr.png)

## Examples album
https://photos.app.goo.gl/KngvSr6ttbyIdFEX2

## User manual (In Russian)
[User manual](https://docs.google.com/document/d/166MPpgo0n661rmQZg7IS_MhNxlCueseOpwgqPBXQ8hI/edit?usp=sharing)

## Cite
[Butov R.A., Drobyishevsky N.I., Moiseenko E.V., Tokarev Yu. N. Mesh generation for radioactive waste management tasks. Radioactive Waste, 2021, no. 1 (14), pp. 87—95. DOI: 10.25283/2587-9707-2021-1-87-95. (In Russian)](http://eng.radwaste-journal.ru/docs/journals/27/mesh_generation_for_radioactive_waste_management_tasks.pdf)

## Contacts
Roman Butov
https://github.com/romanzes637
romanbutov637@gmail.com
