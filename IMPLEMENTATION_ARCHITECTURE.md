# IMPLEMENTATION_ARCHITECTURE

Version: 0.1
Status: APPROVED

## Purpose

Define technology-neutral implementation architecture for Minimal Functional Core.

## Layers

```
Sources
  -> Ingestion Layer
  -> Processing Layer
  -> Knowledge Layer
  -> Analysis Layer
  -> Reporting Layer
```

## Core Principles

- separation of ingestion and analysis;
- persistent provenance;
- replaceable external integrations;
- validation before inference;
- explicit uncertainty.

## Minimal Components

- Source Collector
- Normalizer
- Entity Resolver
- Event Processor
- Verification Engine
- Knowledge Store
- Forecast Engine
- Report Generator

Implementation details are defined only after this architecture is validated.
