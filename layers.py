import torch
import torch.nn.functional as F
import torch.nn as nn
from utils import *
import time

class GAT_gate(torch.nn.Module):
    def __init__(self, n_in_feature, n_out_feature, dropout=0.0, gpu = 0):
        super(GAT_gate, self).__init__()
        self.W = nn.Linear(n_in_feature, n_out_feature)
        #self.A = nn.Parameter(torch.Tensor(n_out_feature, n_out_feature))
        self.A = nn.Parameter(torch.zeros(size=(n_out_feature, n_out_feature)))
        self.input_gate_u = nn.Linear(n_out_feature, 1, bias = False)
        self.input_gate_w = nn.Linear(n_out_feature, 1, bias = False)
        self.forget_gate_u = nn.Linear(n_out_feature, 1, bias = False)
        self.forget_gate_w = nn.Linear(n_out_feature, 1, bias = False)
        self.output_gate_u = nn.Linear(n_out_feature, 1, bias = False)
        self.output_gate_w = nn.Linear(n_out_feature, 1, bias = False)
        self.leakyrelu = nn.LeakyReLU(0.2)
        self.dropout = dropout
        self.zeros = torch.zeros(1)
        if gpu > 0:
            self.zeros = self.zeros.cuda()

    def forward(self, x, adj, get_attention=False):
        h = self.W(x)
        # batch_size = h.size()[0]
        N = h.size()[1]
        e = torch.einsum('ijl,ikl->ijk', (torch.matmul(h,self.A), h))
        e = e + e.permute((0,2,1))
        # zero_vec = -9e15*torch.ones_like(e)
        attention = torch.where(adj > 0, e, self.zeros)
        attention = F.softmax(attention, dim=1)
        #attention = F.dropout(attention, self.dropout, training=self.training)
        #h_prime = torch.matmul(attention, h)
        attention = attention*adj
        h_prime = F.relu(torch.einsum('aij,ajk->aik',(attention, h)))
        # concat = torch.cat([x,h_prime], -1)
        
        input_coeff_u = self.input_gate_u(h_prime)
        # input_coeff_u = F.dropout(input_coeff_u, self.dropout, training=self.training)
        input_coeff_w = self.input_gate_w(x)
        # input_coeff_w = F.dropout(input_coeff_w, self.dropout, training=self.training)
        input_coeff = torch.sigmoid(input_coeff_u + input_coeff_w).repeat(1,1,x.size(-1))
        # input_coeff = F.dropout(input_coeff, self.dropout, training=self.training)

        forget_coeff_u = self.forget_gate_u(h_prime)
        # forget_coeff_u = F.dropout(forget_coeff_u, self.dropout, training=self.training)
        forget_coeff_w = self.forget_gate_w(x)
        # forget_coeff_w = F.dropout(forget_coeff_w, self.dropout, training=self.training)
        forget_coeff = torch.sigmoid(forget_coeff_u + forget_coeff_w).repeat(1,1,x.size(-1))
        # forget_coeff = F.dropout(forget_coeff, self.dropout, training=self.training)

        output_coeff_u = self.output_gate_u(h_prime)
        # output_coeff_u = F.dropout(output_coeff_u, self.dropout, training=self.training)
        output_coeff_w = self.output_gate_w(x)
        # output_coeff_w = F.dropout(output_coeff_w, self.dropout, training=self.training)
        output_coeff = torch.sigmoid(output_coeff_u + output_coeff_w).repeat(1,1,x.size(-1))
        # output_coeff = F.dropout(output_coeff, self.dropout, training=self.training)

        retval = output_coeff * torch.tanh(input_coeff * h_prime + forget_coeff * x)
        if get_attention:
            return retval, attention
        return retval
