from torch import nn
from BiLSTM import BiLSTM


'''
3.1使用BiLSTM
'''

class CTPN_RNN(nn.Module):
    def __init__(self):
        super(CTPN_RNN, self).__init__()
        self.rnn = BiLSTM(input_size=512, hidden_size=128)

    def forward(self, x):
        """
        x: [B, 512, H, W]
        """
        B, C, H, W = x.size()

        # [B, H, W, C]
        x = x.permute(0, 2, 3, 1).contiguous()

        # [B*H, W, C]
        x = x.view(B * H, W, C)

        # [W, B*H, C]
        x = x.permute(1, 0, 2)

        # Bi-LSTM
        x = self.rnn(x)

        # [W, B*H, 256] → [B*H, W, 256]
        x = x.permute(1, 0, 2).contiguous()

        # [B, H, W, 256]
        x = x.view(B, H, W, -1)

        # [B, 256, H, W]
        x = x.permute(0, 3, 1, 2).contiguous()

        return x