import torch
import torch.nn as nn

class Codebook(nn.Module):
    def __init__(self,args):
        super(Codebook, self).__init__()
        self.num_codebook_vectors = args.num_codebook_vectors
        self.latent_dim = args.latent_dim
        self.beta = args.beta
        
        self.embeddings = nn.Embedding(self.num_codebook_vectors,self.latent_dim)
        self.embeddings.weight.data.uniform_(-1.0/self.num_codebook_vectors,1.0/self.num_codebook_vectors)
        

    def forward(self, z):
        z = z.permute(0,2,3,1).contiguous() #putting channels at last
        z_flattened = z.view(-1,self.latent_dim)
        
        #finding the distance between latent dim and codebook vector
        # a^2 + b^2 - 2ab
        d = torch.sum(z_flattened**2,dim=1,keepdim=True) + torch.sum(self.embeddings**2,dim=1) -  2*(torch.matmul(z_flattened,self.embeddings.weight.t()))
        
        min_encoding_indices = torch.argmin(d,dim=1)
        z_q = self.embeddings(min_encoding_indices).view(z.shape)
        
        loss = torch.mean(( z_q.deatch() - z )**2) + self.beta + torch.mean((z_q - z.detach())**2)
        
        z_q = z + (z_q - z).detach()
        
        z_q = z_q.permute(0,3,1,2) #original shape
        
        return z_q,min_encoding_indices,loss
    
            
        