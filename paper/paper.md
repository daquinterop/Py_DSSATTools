---
title: 'DSSATTools: A Python package for crop modeling with DSSAT'
tags:
  - Python
  - agriculture
  - crop modeling
  - crop growth and development models
  - crop simulation
authors:
  - name: Diego Quintero
    orcid: 0000-0003-0336-1875
    affiliation: 1
  - name: Manuel A. Andrade
    affiliation: 2
  - name: Vikalp Mishra
    affiliation: 3
affiliations:
 - name: Wageningen University & Research, The Netherlands
   index: 1
   ror: 00hx57361
 - name: University of Nevada, Reno, NV, USA
   index: 2
 - name: The University of Alabama in Huntsville, Huntsville, AL, USA
   index: 3
date: 2 July 2026
bibliography: paper.bib
---

# Summary

`DSSATTools` is an open-source Python package designed for crop modeling using the Decision Support System for Agrotechnology Transfer (DSSAT) ecosystem. It facilitates the end-to-end crop growth and development modeling pipeline natively in Python. Specifically, `DSSATTools` provides a programmatic wrapper around DSSAT's core simulation engine and features specialized object-oriented classes representing the distinct agronomic entities, soil profiles, environmental records, and management decisions considered during a simulation.

# Statement of need

DSSAT [@Hoogenboom:2019] is a widely recognized software suite incorporating over 45 process-based models for the simulation of crop growth, development, and yield. The Cropping Systems Module (CSM) serves as the primary simulation engine of DSSAT, using multiple sub-modules to simulate individual components of the cropping system (e.g., hydrology, soil dynamics, and genetics). As a legacy Fortran program, the CSM executes via a command-line interface, requiring a rigid set of fixed-width parameters and a simulation configuration file known as the `FILEX`. While the standard desktop distribution for Windows features a Graphical User Interface (GUI) to assist users with file creation, execution, and plotting without text-command exposure, it limits scalability.

In modern agronomic applications, it is increasingly necessary to generate input files, orchestrate simulations, and process high-dimensional outputs programmatically. This requirement is vital for large-scale grid-based crop yield assessments, multi-parameter model calibrations, sensitivity analyses, and the deployment of DSSAT-CSM as a modular component in larger software architectures (such as web tools or web-based decision services). Although the raw CSM supports command-line execution, manually building or modifying input files across dozens of distinct variables is highly error-prone.

`DSSATTools` bridges this gap by acting as a native Python interface to the CSM. It handles the structural requirements of DSSAT inputs and outputs, allowing agricultural scientists, crop modelers, data scientists, and developers to deploy robust modeling pipelines entirely within the Python data-science ecosystem.

# State of the field

Existing efforts to wrap crop simulation models have varied by language and framework. For R users, `DssatR` [@Alderman:2020] provides a functional interface following a traditional scripting paradigm, which remains popular among academic researchers but is less integrated into modern web services or production engineering environments.

Other crop models feature pure Python implementations. For instance, `AquaCrop-OSPy` [@Kelly:2021] implements the AquaCrop model [@Steduto:2009] natively, and the `pcse` (Python Crop Simulation Environment) package [@deWit:2019] encapsulates Wageningen University models like WOFOST. Within the DSSAT landscape, previous automation projects like `PyDSSAT` were released as collections of standalone execution scripts. However, `PyDSSAT` lacked documentation, featured no capabilities for structured input file generation, and development has been completely inactive since 2015.

`DSSATTools` overcomes these limitations by offering a unified, actively maintained, object-oriented ecosystem that handles the complete DSSAT pipeline—from raw data ingestion to post-simulation analysis.

# Software design

Inspired by modern software design patterns observed in `pcse`, `DSSATTools` (Version 3) is structured around a modular, object-oriented framework. The software modules mirror the legacy layout of DSSAT input data files, rendering the architecture intuitive to anyone familiar with the DSSAT GUI tools.

The package is organized into four core modules corresponding to primary DSSAT components:

- **`DSSATTools.soil`**: Manages soil profiles (`SoilProfile` class) and translates structured layers into the required `.SOL` format.
- **`DSSATTools.weather`**: Encapsulates environmental and meteorological observations into a `WeatherStation` class to compile `.WTH` files.
- **`DSSATTools.crop`**: Controls genetic, cultivar, and ecotype parameters across 19 supported crop types (e.g., the `Maize` class) by reading and modifying `.CUL`, `.ECO`, and `.SPE` files.
- **`DSSATTools.filex`**: Models individual experimental treatments and simulation configurations represented within the DSSAT `FILEX`.

Individual operational sequences within the `filex` module are mapped directly to agronomic management events. Single-instance tasks are managed via explicit definitions such as `Planting` or `FertilizerEvent`, while repeated iterations across a season are collected into structured containers like `Fertilizer`. Global operational directives are configured using the `SimulationControls` class.

Simulations are executed by creating an instance of the `DSSAT` environment, which handles the secure setup and tear-down of low-level scratch directories, protecting execution states during parallel execution. Isolated single-treatment runs are dispatched via the `run_treatment()` method, which outputs structured `pandas.DataFrame` execution tables and native text strings representing standard outputs like `PlantGro` and `OVERVIEW`.

# Research impact statement

`DSSATTools` has been integrated into a variety of peer-reviewed research areas involving digital agriculture, climate resilience, and automated workflows. It has facilitated high-throughput automated calibration pipelines across expansive geographic boundaries [@Quintero:2024; @Quintero:2025] and enabled evaluations of climate-resilient crop ideotypes under variable management practices [@Srivastava:2026]. Additionally, the package has served as a critical execution engine for modern decision support systems, such as coupling biophysical crop simulations with Large Language Models (LLMs) to power conversational AI agents for agricultural decision-making [@Kpodo:2026], and conducting regional risk management and intervention assessments [@Quintero:2023].

# AI usage disclosure

During the preparation of this manuscript, a generative AI model (Gemini by Google) was utilized strictly to refine technical terminology, improve narrative flow, and audit the Markdown structural formatting for compliance with journal layout standards. The authors maintain ultimate accountability for the intellectual content and factual accuracy of this paper.

# References