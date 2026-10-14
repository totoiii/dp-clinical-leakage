# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from typing import Optional

import numpy as np
from scipy import optimize
from transformers import TrainingArguments as HfTrainingArguments
from transformers import IntervalStrategy, logging
from dataclasses import dataclass, field
from datasets.utils import disable_progress_bar
from prv_accountant import Accountant

logger = logging.get_logger(__name__)


@dataclass
class PrivacyArguments:
    per_sample_max_grad_norm: Optional[float] = field(default=None, metadata={"help": "Max per sample clip norm"})
    noise_multiplier: Optional[float] = field(default=None, metadata={"help": "Noise multiplier for DP training"})
    target_epsilon: Optional[float] = field(default=None, metadata={
        "help": "Target epsilon at end of training (mutually exclusive with noise multiplier)"
    })
    target_delta: Optional[float] = field(default=None, metadata={
        "help": "Target delta, defaults to 1/N"
    })
    disable_dp: bool = field(default=False, metadata={
        "help": "Disable DP training."
    })

    def initialize(self, sampling_probability: float, num_steps: int, num_samples: int) -> None:
        if self.target_delta is None:
            self.target_delta = 1.0/num_samples
        logger.info(f"The target delta is set to be: {self.target_delta}")

        # Set up noise multiplier
        if self.noise_multiplier is None:
            self.noise_multiplier = find_noise_multiplier(
                sampling_probability=sampling_probability,
                num_steps=num_steps,
                target_delta=self.target_delta,
                target_epsilon=self.target_epsilon
            )
        logger.info(f"The noise multiplier is set to be: {self.noise_multiplier}")

    @property
    def is_initialized(self) -> bool:
        return (
            self.per_sample_max_grad_norm is not None and
            self.noise_multiplier is not None and
            self.target_delta is not None
        )

    def __post_init__(self):
        if self.disable_dp:
            logger.warning("Disabling differentially private training...")
            self.noise_multiplier = 0.0
            self.per_sample_max_grad_norm = float('inf')
            self.target_epsilon = None
        else:
            if bool(self.target_epsilon) == bool(self.noise_multiplier):
                raise ValueError("Exactly one of the arguments --target_epsilon and --noise_multiplier must be used.")
            if self.per_sample_max_grad_norm is None:
                raise ValueError("DP training requires --per_sample_max_grad_norm argument.")


@dataclass
class TrainingArguments(HfTrainingArguments):
    dry_run: bool = field(
        default=False,
        metadata={"help": "Option for reducing training steps (2) and logging intervals (1) for quick sanity checking of arguments."}
    )

    def __post_init__(self):
        super().__post_init__()
        if self.dry_run:
            logger.warning("--dry_run was specified. Reducing number of training steps to 2 and logging intervals to 1...")
            self.logging_steps = 1
            self.logging_strategy = IntervalStrategy.STEPS
            self.eval_steps = 1
            self.evaluation_strategy = IntervalStrategy.STEPS

            self.max_steps = 2

        if self.disable_tqdm:
            disable_progress_bar()


def find_noise_multiplier(sampling_probability: float, num_steps: int, target_epsilon: float, target_delta: float,
                          eps_error: float=0.1) -> float:
    """
    Find a noise multiplier that satisfies a given target epsilon.

    dpleak patch: the upstream bracket + Brent search calls the PRV accountant at
    noise levels where its discretisation raises ("Discrete mean differs from
    continuous mean"), depending on the numpy/BLAS build. This version bisects
    on mu, treating a failed evaluation as epsilon = inf (too little noise), and
    returns the smallest mu (to 1e-4 relative) whose PRV upper bound on epsilon is
    <= target_epsilon. The result is checked against the PRV upper bound.

    :param float sampling_probability: Probability of a record being in batch for Poisson sampling
    :param int num_steps: Number of optimisation steps
    :param float target_epsilon: Desired target epsilon
    :param float target_delta: Value of DP delta
    :param float eps_error: Error allowed for final epsilon
    """
    def eps_upper(mu: float) -> float:
        try:
            acc = Accountant(
                noise_multiplier=mu,
                sampling_probability=sampling_probability,
                delta=target_delta,
                max_compositions=num_steps,
                eps_error=eps_error/2
            )
            return acc.compute_epsilon(num_steps)[2]
        except (OverflowError, RuntimeError, ValueError):
            return float('inf')

    lo, hi = 0.05, 1.0
    while eps_upper(hi) > target_epsilon:
        lo, hi = hi, hi * 2
        if hi > 100.0:
            raise RuntimeError("Finding a suitable noise multiplier has not converged. "
                               "Try increasing target epsilon or decreasing sampling probability.")
    while (hi - lo) / hi > 1e-4:
        mid = 0.5 * (lo + hi)
        if eps_upper(mid) > target_epsilon:
            lo = mid
        else:
            hi = mid
    assert eps_upper(hi) <= target_epsilon
    return hi
