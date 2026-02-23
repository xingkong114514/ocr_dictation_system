from CTPN import CTPN
from torch.utils.data import Dataset
import os
class CTPNDataset(Dataset):
    def __init__(self,datadir,labelsdir):
        if not os.path.isdir(datadir):
            raise Exception('[ERROR] {} is not a directory'.format(datadir))
        if not os.path.isdir(labelsdir):
            raise Exception('[ERROR] {} is not a directory'.format(labelsdir))
        self.datadir = datadir
        self.labelsdir = labelsdir
        self.img_names =os.listdir(self.datadir)

    def __len__(self):
        return len(self.img_names)



def reshape_pred(cls_pred, reg_pred, num_anchors=10):
    B, _, H, W = cls_pred.shape

    cls_pred = cls_pred.permute(0, 2, 3, 1).contiguous()
    cls_pred = cls_pred.view(-1, 2)

    reg_pred = reg_pred.permute(0, 2, 3, 1).contiguous()
    reg_pred = reg_pred.view(-1, 2)

    return cls_pred, reg_pred





model=CTPN().cuda()
model.train()
num_epochs = 10
for epoch in range(num_epochs):
    for images, gt_boxes in dataloader:
        images = images.cuda()

        cls_pred, reg_pred = model(images)
        cls_pred, reg_pred = reshape_pred(cls_pred, reg_pred)

        cls_target, reg_target = assign_targets(anchors, gt_boxes)

        loss = criterion(cls_pred, reg_pred, cls_target, reg_target)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    print(f"Epoch {epoch}, Loss: {loss.item():.4f}")
cls_pred, reg_pred = model(images)