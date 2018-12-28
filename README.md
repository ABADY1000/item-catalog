# FSND Item Catalog (Project2)

  This project is example of routing through a web application and giving the 
  authorized users the possibility to add, edit and delete restaurant and items

## Getting Started

  This web application is bult to show and modify database content, so it requires a data base first to work on.

  this tool works only on FSND "restaurantmenu" database.

### Prerequisites

  You will need the following:
  * Virtual Machine softwere.
  * Vgrant with Ubuntu installed.
  
  You can download VM from [here](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1)  
  And you cand download Vagrant [here](https://www.vagrantup.com/downloads.html)

  Inside your new environment *Ubuntu* you will need:
  * Python 3.6.
  * Flask (web framework).
  * sqlalchemy (SQL api).
  
  
### Installing

  After downloading this project add it tou your Vagrant files, run Vagrant 
```
$ vagrant up
```
  and then
```
$ vagrant ssh
```
Switch the path to the files you have just added and run it using Python 3.6
```
$ Python3 [your file name]
```

After you do so, run your browser and goto (localhost:8000/),
you should be able to see the main page (Restaurant Page)

you are free now to brows the app


## Code Styling

Pyhton code is wrtitten according to [pep8](https://www.python.org/dev/peps/pep-0008/)

and the code is tested to be applicable for this styling method using the library [pycodestyle](https://pycodestyle.readthedocs.io/en/latest/)

To run the test use
~~~
$ pycodestyle [your file name]
~~~
and there should be no output if your code is well styled.


## Author

* **Abdullah Alamoodi** - [Github](https://github.com/abady1000)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* **Mashael ElSaeed** - Course instructor
