from pathlib import Path
from setuptools import setup, find_packages


def find_version() -> str:
    version = "0.0.65"
    extension_yaml_path = Path(__file__).parent / "extension" / "extension.yaml"
    try:
        with open(extension_yaml_path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("version"):
                    version = line.split(" ")[-1].strip("\"")
                    break
    except Exception:
        pass
    return version


from setuptools import setup, find_packages

setup(name="insightify",
      version="0.0.65",
      description="Insightify python EF2 extension",
      author="Dynatrace",
      packages=find_packages(),
      python_requires=">=3.10",
      include_package_data=True,
      install_requires=["dt-extensions-sdk", "requests<3", "charset_normalizer<3"],
      extras_require={"dev": ["dt-extensions-sdk[cli]"]},
      package_data={"insightify": ["constant/*"]},
      )
