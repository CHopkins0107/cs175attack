from typing import List, Iterator, Dict, Tuple, Any, Type

import numpy as np
import torch
from copy import deepcopy

np.random.seed(1901)

class Attack:
    def __init__(
        self,
        vm, device, attack_path,
        min_val = 0,
        max_val = 1
    ):
        """
        args:
            vm: virtual model is wrapper used to get outputs/gradients of a model.
            device: system on which code is running "cpu"/"cuda"
            min_val: minimum value of each element in original image
            max_val: maximum value of each element in original image
                     each element in perturbed image should be in the range of min_val and max_val
            attack_path: Any other sources files that you may want to use like models should be available in ./submissions/ folder and loaded by attack.py. 
                         Server doesn't load any external files. Do submit those files along with attack.py
        """
        self.vm = vm
        self.device = device
        self.attack_path = attack_path
        self.min_val = 0
        self.max_val = 1

    def attack(
        self, original_images: np.ndarray, labels: List[int], target_label = None,
    ):
        original_images = original_images.to(self.device)
        original_images = torch.unsqueeze(original_images, 0)
        labels = torch.tensor(labels).to(self.device)
        target_labels = target_label * torch.ones_like(labels).to(self.device)
        perturbed_image = original_images
        
        # -------------------- TODO ------------------ #

        # Modified by Nathan on 4/21
        # Iterative Least-Likely Class Method
        # Initialize some epsilon and alpha
        e = 5
        epsilon = min(e+4, int(1.25*e))
        alpha = 0.01
        # e = 5 and alpha = 0.01 worked best for me, yielding:
        # attacker_success_rate: 100, dist: 6.228, score: 91.5358

        # Desired label is the label we want to output (Label 1)
        desired_labels = torch.tensor([torch.tensor(1)]).to(self.device)

        # Iterate
        for i in range(epsilon):
            # Calculate the gradient with respect to the desired label
            gradient = self.vm.get_batch_input_gradient(perturbed_image, desired_labels)
            # Modify the perturbed image by the sign of the gradient
            perturbed_image = perturbed_image - (alpha*gradient.sign())
            # Clamp the image so it is in the range of the minimum and maximum value
            perturbed_image = torch.clamp(perturbed_image, self.min_val, self.max_val)
            # Use the X_{n} image to calculate the X_{n+1} image
            perturbed_image = perturbed_image.detach().clone()


        # ------------------ END TODO ---------------- #

        adv_outputs = self.vm.get_batch_output(perturbed_image)
        final_pred = adv_outputs.max(1, keepdim=True)[1]
        correct = 0
        correct += (final_pred == target_labels).sum().item()
        return np.squeeze(perturbed_image.cpu().detach().numpy()), correct
