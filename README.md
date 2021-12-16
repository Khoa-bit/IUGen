<p align="center">
    <img src="assets/Banner@1x.png" alt="IUGen Banner and Logo">
</p>

---

IUGen is a modern, user-friendly script for generating schedules that assists with the IU semester registration.

---
## Installation

```console
$ pip install -r requirements.txt

---> 100%
```

## How to use
+ Duplicate `Template_catalog.ods` in `inputs` folder.
+ Name the new duplicate file `catalog.ods` or `catalog.xlsx`.
+ Fill it with classes data from [IU Edusoftweb](https://edusoftweb.hcmiu.edu.vn/)
  + Tips: Follow the 2 example files `Example_catalog_1.ods` and `Example_catalog_2.ods` to successfully input your classes' data.
+ Select the classes that you want to participate in by flagging it with `*`.
+ Run the `main.py` script.
  ```console
  $ python main.py
  or
  $ python3 main.py
  
  ---> 100%
  ```
+ The script will output to `results/schedule.xlsx`




