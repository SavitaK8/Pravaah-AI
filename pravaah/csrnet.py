"""CSRNet (Li et al., CVPR 2018): VGG16 frontend + dilated-conv backend -> density map. Needs requirements-ml.txt."""
import torch
import torch.nn as nn
from torchvision import models

MEAN, STD = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)


class CSRNet(nn.Module):
    def __init__(self, pretrained_frontend=False):
        super().__init__()
        vgg = models.vgg16(weights="IMAGENET1K_V1" if pretrained_frontend else None)
        self.frontend = nn.Sequential(*list(vgg.features.children())[:23])
        layers, c = [], 512
        for v in (512, 512, 512, 256, 128, 64):
            layers += [nn.Conv2d(c, v, 3, padding=2, dilation=2), nn.ReLU(inplace=True)]
            c = v
        self.backend = nn.Sequential(*layers)
        self.out = nn.Conv2d(64, 1, 1)

    def forward(self, x):
        return torch.relu(self.out(self.backend(self.frontend(x))))


def load(weights_path, device="cpu"):
    model = CSRNet()
    ck = torch.load(weights_path, map_location=device)
    model.load_state_dict(ck.get("state_dict", ck))
    return model.to(device).eval()


@torch.no_grad()
def density(model, frame_bgr, device="cpu"):
    """frame_bgr: HxWx3 uint8 (OpenCV). Returns a 2-D numpy density map (its sum ~ people count)."""
    import cv2
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB).astype("float32") / 255
    t = torch.from_numpy(rgb).permute(2, 0, 1)
    t = (t - torch.tensor(MEAN)[:, None, None]) / torch.tensor(STD)[:, None, None]
    return model(t[None].to(device))[0, 0].cpu().numpy()
