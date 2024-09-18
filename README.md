<a id="readme-top"></a>

<br />
<div align="center">
  <button onclick="toggleImages()">Style</button>
  <a href="https://github.com/josiahlucerodev/nactemplate">
    <img src="https://github.com/josiahlucerodev/nalogos/blob/main/projects/nactemplate/nactemplate.svg" 
      alt="Logo" style="display: none;" width="80" height="80", id="nonrounded">
    <img src="https://github.com/josiahlucerodev/nalogos/blob/main/projects/nactemplate/nactemplate_round.svg" 
      alt="Logo" style="display: block;" width="80" height="80", id="rounded">
  </a>
  <h3 align="center">Cpp config template</h3>
  <script>
    function toggleImages() {
      const img1 = document.getElementById('nonrounded');
      const img2 = document.getElementById('rounded');
      if (img1.style.display === 'none') {
        img1.style.display = 'block';
        img2.style.display = 'none';
      } else {
        img1.style.display = 'none';
        img2.style.display = 'block';
      }
    }
  </script>
</div>

## About 
This project (nactemplate) provides a template for the configuration of the cpp programming langauage and is the primary template for the novo affect software stack. 

Whats Provided:
* Header and Source scanner 
* Default presents for windows, linux, and web
* util functions for configerations 

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Dependences
* python
* cmake

<p align="right">(<a href="#readme-top">back to top</a>)</p>