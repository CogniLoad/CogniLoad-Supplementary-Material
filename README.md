<div align="center">

<img src="https://github.com/CogniLoad/CogniLoad.github.io/blob/main/paper_logo.png" width="120px"/>

### Do Large Language Models Suffer from Cognitive Overload? A Benchmark and Orchestration Framework

<div>

[![Project Website](https://img.shields.io/badge/🌐-Project%20Website-0066CC?style=for-the-badge)](https://cogniload.github.io/)
</div>

---

</div>

## 📌 Overview

<div align="center">

> **CogniLoad** is an experimental framework designed to research and mitigate **Cognitive Overload** in Large Language Models (LLMs) when processing complex, redundant, or contradictory information streams.

</div>

At its core, the project utilizes the **Collective Orchestration Framework (COF)**, which simulates a multi-expert collaborative environment. By implementing **Task Decomposition**, **Collective Memory**, and **Iterative Refinement**, CogniLoad significantly enhances the logical stability and accuracy of models under extreme cognitive pressure.

<div align="center">

> 💡 **Important:** This research is currently prepared for submission to **ACL 2026**.

</div>

<div align="center">

</div>

---

## ✨ Key Features

<div align="center">

### 🚀 Core Capabilities

</div>

<table>
<tr>
<td width="50%" valign="top">

#### 🤝 Collective Orchestration Framework (COF)

Employs a multi-agent architecture to decompose complex queries into specialized sub-tasks with unique **"Analytical Styles"**.

#### 💾 Collective Memory System

A global state store that allows agents to share intermediate reasoning, preventing single-agent logic failure caused by excessive context or information density.

</td>
<td width="50%" valign="top">

#### 🧪 Stress Test Benchmarking

An expanded suite based on the `C-Eval` dataset, featuring a multidimensional load matrix with repetition and interference loads.

#### 🛡️ Robust Implementation

Native support for **DeepSeek-R1** (utilizing Thinking Processes) and **Qwen3** series. Industrial-grade pipeline with **Multi-API Key Rotation**, **Exponential Backoff**, and automated network diagnostics.

</td>
</tr>
</table>

**Load Matrix Details:**

- **🔄 Repetition Load:** 25x, 50x, 75x, and 100x redundant inputs
- **⚡ Interference Load:** Levels 1–4 of Ambiguity, Contradiction, and Irrelevant information

---

## 🛠️ Getting Started

### 📦 1. Requirements

<div align="center">

| Requirement | Version/Specification |
|:-----------:|:---------------------:|
| **Python** | 3.8+ |
| **API Credentials** | ModelScope API Token or OpenAI-compatible API |

</div>

Install the necessary dependencies:

```bash
pip install openai tqdm
```

### ⚙️ 2. Configuration

Configure your API key pool and execution mode in the main script. The system automatically manages request pacing and performs dynamic key switching upon rate-limit detection.

<details>
<summary><b>📝 Click to view configuration example</b></summary>

```python
# API Key Pool (Automatic rotation and cooldown management)
api_keys = [
    'your-modelscope-api-token-1',
    'your-modelscope-api-token-2',
    'your-modelscope-api-token-3'
]

# Core Framework Settings
USE_COF_FRAMEWORK = True  # True: Enable Multi-agent COF; False: Baseline mode
MAX_WORKERS = 1           # Adjust based on your API rate limits
```

</details>

### ▶️ 3. Execution

Run the evaluation pipeline:

```bash
python run_eval.py
```

### 📂 4. Dataset & Load Matrix

The framework evaluates LLM cognitive boundaries through the following standardized stress-test files:

<div align="center">

| **Dimension** | **Filename Prefix** | **Load Levels** |
|:-------------:|:-------------------:|:---------------:|
| 🎯 **Baseline** | `C-Eval_standardized` | Standard Benchmarking |
| 🔄 **Repetition** | `C-Eval_repeated_question_` | 25x, 50x, 75x, 100x |
| ❓ **Ambiguity** | `ambiguity-load-level-` | Level 1, 2, 3, 4 |
| ⚠️ **Contradictory** | `contradictory-load-level-` | Level 1, 2, 3, 4 |
| 🗑️ **Irrelevant** | `irrelevant-load-level-` | Level 1, 2, 3, 4 |

</div>

---

## 🧠 Framework Logic

<div align="center">

The COF reasoning process is defined by the following stages:

</div>

### 1. Decomposition

<div align="center">

The Orchestrator splits Query $Q$ into $N$ specialized perspectives:

</div>

```
f_dec(Q) → {P₁, P₂, ..., Pₙ}
```

$$
f_{dec}(Q) \rightarrow \{P_1, P_2, ..., P_N\}
$$

### 2. Collective Memory

<div align="center">

During each iteration $t$, all agent outputs are stored in the collective memory $M$:

</div>

```
M_t = {O_{1,t}, O_{2,t}, ..., O_{N,t}}
```

$$
M_t = \{O_{1,t}, O_{2,t}, ..., O_{N,t}\}
$$

### 3. Iterative Refinement

<div align="center">

Agents refine their logic based on peer insights from $M_{t-1}$:

</div>

```
O_{i,t} = f_agent(Q, P_i, O_{i,t-1}, M_{t-1})
```

$$
O_{i,t} = f_{agent}(Q, P_i, O_{i,t-1}, M_{t-1})
$$

### 4. Synthesis

<div align="center">

The Orchestrator synthesizes all reasoning chains into a final structured JSON output.

</div>

---


---


<div align="center">

### 🌐 Project Website

**[https://cogniload.github.io/](https://cogniload.github.io/)**

<div align="center">


</div>

</div>
