from torch import nn
import torch

'''
6-Anchor标签及loss设计
'''
class CTPNLoss(nn.Module):
    def __init__(self):
        super(CTPNLoss, self).__init__()
        self.cls_loss = nn.CrossEntropyLoss(ignore_index=-1)
        self.reg_loss = nn.SmoothL1Loss()

    def forward(self, cls_pred, reg_pred, cls_target, reg_target):
        """
        cls_pred: [N, 2]
        reg_pred: [N, 2]
        cls_target: [N] (1, 0, -1)
        reg_target: [N, 2]
        """

        # 分类 loss（自动忽略 -1）
        loss_cls = self.cls_loss(cls_pred, cls_target)

        # 回归 loss（只对正样本）
        pos_mask = cls_target == 1
        if pos_mask.sum() > 0:
            loss_reg = self.reg_loss(
                reg_pred[pos_mask],
                reg_target[pos_mask]
            )
        else:
            loss_reg = torch.tensor(0.0, device=cls_pred.device)

        return loss_cls + loss_reg