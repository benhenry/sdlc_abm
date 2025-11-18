# sdlc_abm
An attempt at an agent based model (ABM) for the SW development lifecycle (SDLC) using DX Core 4 key metrics
as well as my experience working with engineering teams at scale for years.

## Features
MVP will be a form with fields covering all of the independent variables needed to track. It will
use these variables and iterations to show features, bugs, incidents, average load on developers
at various levels, etc. 

### DX Metrics to track

  * Diffs per Engineering
  * Developer Experience Index (or equivalent)
  * Change failure rate
  * Percentage of time spent on new capabilities

### Secondary metrics

  * Lead time
  * Deployment frequency
  * Perceived rate of delivery
  * Time to 10th PR
  * Ease of delivery
  * Regrettable attrition
  * Failed deployment recovery time
  * Perceived software quality
  * Operational health and security metrics
  * Initative progress and ROI
  * Revenue per engineer
  * R&D as percentage of revenue

## Tech Stack
This project will use Python and React with MySQL as a backend, if needed. SQLlite for dev version of
the app, and GCP to host.

I'll be using Claude Code nearly exclusively to develop this project, but to achieve my learning goals,
I will be doing some hand tuning in areas where I aim to learn.

## Learning Goals
I want to build a second project with Claude Code (bghenry.com for the first), but I want to do more 
interation with the actual code layer in this project. I'd like to learn more about React,
systems design, ABMs, and I might over engineer some aspects in order to learn about Docker and k8s. This project is primarily a learning experiment for me, but it also will build something I've wanted to
build for the last few years, but haven't had time.
