import torch
import torch.nn.functional as F
from torchvision import models  # type: ignore

from app.domain.interfaces.model import IVictimModel


class ResNet50VictimModel(IVictimModel):
    def __init__(self) -> None:
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # Load weights explicitly to avoid warnings
        weights = models.ResNet50_Weights.DEFAULT
        self._model = models.resnet50(weights=weights).to(self._device)
        self._model.eval()

    @property
    def device(self) -> torch.device:
        return self._device

    def forward(self, tensor: torch.Tensor) -> torch.Tensor:
        tensor = tensor.to(self._device)
        return self._model(tensor)

    def predict(self, tensor: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            logits = self.forward(tensor)
            return F.softmax(logits, dim=1)

    def compute_gradients(self, tensor: torch.Tensor, *args, **kwargs) -> torch.Tensor:
        tensor = tensor.to(self._device)
        if not tensor.requires_grad:
            tensor.requires_grad_(True)
        tensor.retain_grad()
            
        logits = self.forward(tensor)
        target = logits.max(1, keepdim=True)[1].squeeze()
        if target.ndim == 0:
            target = target.unsqueeze(0)
            
        loss = F.cross_entropy(logits, target)
        self._model.zero_grad()
        loss.backward()
        
        grad = tensor.grad
        if grad is None:
            return torch.zeros_like(tensor)
        return grad

    def zero_grad(self) -> None:
        self._model.zero_grad()
