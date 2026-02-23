from torch import nn


'''
3.BiLstm实现
'''


class BiLSTM(nn.Module):
    def __init__(self, input_size=512, hidden_size=128):
        super(BiLSTM, self).__init__()

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=1,
            bidirectional=True,
            batch_first=False
        )

    def forward(self, x):
        """
        x: [W, B*H, 512]
        """
        out, _ = self.lstm(x)
        return out