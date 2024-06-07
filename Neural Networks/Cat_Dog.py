# 1.导入所需的库和模块：
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader
import os
from PIL import Image
# 设置随机种子以确保结果可重现
torch.manual_seed(42)
# 2.定义训练集和测试集的路径：
cat_train_dataset = "./catsdogs/train/Cat"
dog_train_dataset = "./catsdogs/train/Dog"
cat_test_dataset = "./catsdogs/test/Cat"
dog_test_dataset = "./catsdogs/test/Dog"
# 3.定义自定义的数据集类：
"""
(1)定义了一个名为 CatDogDataset 的数据集类，该类继承自 Dataset 类，表示它是一个PyTorch的数据集类。
(2)__init__(self, cat_dataset, dog_dataset, transform=None) 是数据集类的初始化方法。在初始化过程中，接收两个参数 cat_dataset 和 dog_dataset，分别表示猫和狗数据集的路径。transform 参数是一个可选的数据预处理操作，用于对图像进行转换。
(3)在初始化方法中，将传入的参数分别保存到类的成员变量中，即 self.cat_dataset 和 self.dog_dataset。
(4)self.transform 保存了数据预处理操作。
(5)self.cat_file_list 和 self.dog_file_list 是通过调用 load_file_list() 方法加载对应数据集文件夹中的文件列表。
(6)load_file_list(self, dataset_path) 方法用于加载指定数据集路径下的文件列表。通过 os.listdir() 函数获取路径下所有文件的文件名，并返回文件列表。
(7)__len__(self) 方法返回数据集的样本数量。这里通过累加猫和狗的文件列表长度得到总样本数量。
(8)__getitem__(self, idx) 方法用于根据给定的索引 idx 获取数据集中的一个样本。根据索引值判断样本属于猫类还是狗类，并获取对应的图像路径和标签。
(9)如果索引小于猫文件列表长度，表示该样本属于猫类。通过 os.path.join() 函数将猫数据集路径和对应的文件名拼接成完整的图像路径。标签 label 设置为 0，表示猫类。
(10)否则，索引值大于等于猫文件列表长度，表示该样本属于狗类。通过 os.path.join() 函数将狗数据集路径和对应的文件名拼接成完整的图像路径。标签 label 设置为 1，表示狗类。
(11)使用 PIL.Image.open() 打开图像，并通过 convert("RGB") 方法将图像转换为 RGB 模式，保证图像具有三个通道。
(12)如果定义了数据预处理操作 self.transform，则对图像进行相应的转换操作。
(13)最后返回图像和标签，表示一个样本的数据。
"""
class CatDogDataset(Dataset):
    def __init__(self, cat_dataset, dog_dataset, transform=None):
        self.cat_dataset = cat_dataset
        self.dog_dataset = dog_dataset
        self.transform = transform
        self.cat_file_list = self.load_file_list(self.cat_dataset)
        self.dog_file_list = self.load_file_list(self.dog_dataset)
    def load_file_list(self, dataset_path):
        self.dataset_path = dataset_path
        file_list = os.listdir(dataset_path)
        return file_list
    def __len__(self):
        return len(self.cat_file_list) + len(self.dog_file_list)
    def __getitem__(self, idx):
        if idx < len(self.cat_file_list):
            img_path = os.path.join(self.cat_dataset, self.cat_file_list[idx])
            label = 0
        else:
            img_path = os.path.join(self.dog_dataset, self.dog_file_list[idx - len(self.cat_file_list)])
            label = 1

        label = torch.as_tensor(label, dtype=torch.int64)  # 必须使用long 类型数据，否则后面训练会报错 expect long
        # img_path = os.path.join(self.dataset_path, img_path)
        image = Image.open(img_path).convert("RGB")
        # image = self.transform(image)
        if self.transform is not None:
            image = self.transform(image)
        return image, label
# 数据预处理和增强
# 4.定义数据预处理的转换操作：
"""
(1)transforms.Compose() 函数用于将多个数据转换操作组合在一起，形成一个数据转换的管道。
(2)transforms.Resize((32, 32)) 是一个数据转换操作，用于将图像的大小调整为指定的尺寸 (32, 32)。这里将图像调整为宽度和高度均为 32 像素的正方形。
(3)transforms.ToTensor() 是一个数据转换操作，用于将图像转换为张量（Tensor）形式。它将图像的像素值范围从 0-255 缩放到 0-1，并将通道顺序从 H x W x C 转换为 C x H x W，其中 C 表示通道数。
(4)transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)) 是一个数据转换操作，用于对图像进行标准化。这里通过减去均值 0.5 并除以标准差 0.5 来将图像的像素值标准化到均值为 0、标准差为 1 的范围内。这个操作有助于提高模型的训练稳定性和收敛速度。
(5)定义了 transform 变量，将以上的数据转换操作组合在一起。
(6)trainloader 和 testloader 是用于加载训练集和测试集数据的 DataLoader 对象，但是在当前代码片段中，它们被初始化为一个空列表。可能是之后的代码将数据加载到这些列表中，以便进行训练和测试。
"""
transform = transforms.Compose([
    transforms.Resize((64, 64)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])
"""
(1)train_dataset = CatDogDataset(cat_train_dataset, dog_train_dataset, transform=transform) 创建一个训练集对象 train_dataset，通过实例化 CatDogDataset 类并传入猫和狗训练集的路径以及数据预处理操作 transform。
(2)test_dataset = CatDogDataset(cat_test_dataset, dog_test_dataset, transform=transform) 创建一个测试集对象 test_dataset，通过实例化 CatDogDataset 类并传入猫和狗测试集的路径以及数据预处理操作 transform。
(3)trainloader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=2) 创建一个训练集的数据加载器 trainloader，通过实例化 DataLoader 类并传入训练集对象 train_dataset，设置批量大小为 32，打乱数据顺序（shuffle=True），并使用 2 个工作线程加载数据（num_workers=2）。
(4)testloader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=2) 创建一个测试集的数据加载器 testloader，通过实例化 DataLoader 类并传入测试集对象 test_dataset，设置批量大小为 32，不打乱数据顺序（shuffle=False），并使用 2 个工作线程加载数据（num_workers=2）。
这些代码的目的是将预处理后的训练集和测试集数据加载到相应的数据加载器中，以便在训练和测试过程中批量地获取数据供模型使用。训练集和测试集中的图像会被分批次地加载到模型中进行训练和评估。数据加载器提供了对数据的迭代和批处理的功能，方便了模型的训练和评估过程。
"""
train_dataset = CatDogDataset(cat_train_dataset, dog_train_dataset, transform=transform)
valid_dataset = CatDogDataset(cat_test_dataset, dog_test_dataset, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True, num_workers=4)
valid_loader = DataLoader(valid_dataset, batch_size=16, shuffle=False, num_workers=4)
# 定义CNN模型
"""
(1)定义了一个名为 CatDogClassifier 的神经网络模型，该模型继承自 nn.Module，表示它是一个PyTorch的模块。
(2)__init__(self) 函数是模型的初始化方法。在初始化过程中，首先调用了 super() 函数，用于调用父类的 __init__() 方法，确保父类的初始化被执行。
(3)接下来定义了几个网络层。self.conv1 是一个卷积层，nn.Conv2d(3, 16, 3) 表示输入通道数为 3，输出通道数为 16，卷积核大小为 3x3。这里的 3 表示图像的 RGB 通道数。
(4)self.conv2 是第二个卷积层，nn.Conv2d(16, 32, 3) 表示输入通道数为 16，输出通道数为 32，卷积核大小为 3x3。
(5)self.fc1 是一个全连接层，nn.Linear(32 * 6 * 6, 256) 表示输入特征维度为 32x6x6，输出特征维度为 256。
(6)self.fc2 是最后一层全连接层，nn.Linear(256, 2) 表示输入特征维度为 256，输出特征维度为 2。这里的 2 表示模型的输出类别数，即猫和狗两类。
(7)forward(self, x) 函数定义了模型的前向传播过程。输入 x 表示模型的输入数据。在前向传播过程中，输入数据通过卷积层和池化层进行特征提取，然后通过全连接层进行分类。具体的操作如下：
    通过 nn.functional.relu() 函数对输入数据 x 进行 ReLU 激活函数的操作，这里分别对 self.conv1 和 self.conv2 的输出进行激活。
    通过 nn.functional.max_pool2d() 函数对卷积层的输出进行最大池化操作，其中参数 2 表示池化窗口大小为 2x2。
    将池化层的输出通过 x.view(x.size(0), -1) 转换为一维向量，用于传递给全连接层。
    通过 nn.functional.relu() 函数对全连接层 self.fc1 的输出进行激活。
    最后通过全连接层 self.fc2 得到模型的输出结果，这里没有经过激活函数。
(8)返回模型的输出 x。该输出表示模型对输入数据的预测结果，对应两个类别的得分。
"""
class CatDogClassifier(nn.Module):
    def __init__(self):
        super(CatDogClassifier, self).__init__()
        self.conv_layers = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        self.fc_layers = nn.Sequential(
            nn.Linear(128 * 8 * 8, 512),
            nn.ReLU(),
            nn.Linear(512, 2),
            nn.LogSoftmax(dim=1)
        )
    def forward(self, x):
        x = self.conv_layers(x)
        x = x.view(x.size(0), -1)
        x = self.fc_layers(x)
        return x
# 初始化模型
"""
(1)net = CatDogClassifier() 创建一个模型对象 net，通过实例化 CatDogClassifier 类来构建模型。
(2)device = torch.device("cuda" if torch.cuda.is_available() else "cpu") 根据可用的硬件设备情况，将设备选择为 GPU（如果可用）或 CPU。这个代码行用于设定模型训练和推理所使用的设备。
(3)net = net.to(device) 将模型 net 移动到所选的设备上，以便在该设备上进行计算。
(4)criterion = nn.CrossEntropyLoss() 创建一个损失函数对象 criterion，使用交叉熵损失函数，该函数在分类任务中常被用于衡量模型的输出与真实标签之间的差异。
(5)optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9) 创建一个优化器对象 optimizer，使用随机梯度下降（SGD）优化算法来更新模型的参数。net.parameters() 返回模型中可训练的参数列表，这些参数将被优化器更新。lr=0.001 设置学习率为 0.001，控制参数更新的步长。momentum=0.9 设置动量参数为 0.9，用于加速模型在训练过程中的收敛。
(6)net.train() 将模型设置为训练模式。这一步是为了确保模型中的一些特定层（如 Dropout 或 Batch Normalization）在训练过程中起作用，并在推理时处于关闭状态。
"""
model = CatDogClassifier()
# 定义损失函数和优化器
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)
# 训练模型
num_epochs = 5
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)
"""
(1)if __name__ == '__main__': 这行代码用于判断当前脚本是否为主脚本，即直接被运行的脚本，而不是作为模块被导入的脚本。这样做是为了确保下面的代码只在主脚本中执行，而不是在被导入时执行。
(2)for epoch in range(5): 这个循环用于迭代训练过程，执行5个训练周期（epoch）。
(3)running_loss = 0 初始化一个变量 running_loss，用于累计每个训练周期的损失值。
(4)for inputs, labels in trainloader: 这个循环用于遍历训练集数据加载器，每次迭代返回一个批次的输入数据 inputs 和对应的标签 labels。
(5)inputs = inputs.to(device) 将输入数据 inputs 移动到所选的设备上，以便在该设备上进行计算。
(6)labels = labels.to(device) 将标签数据 labels 移动到所选的设备上。
(7)optimizer.zero_grad() 清零优化器中之前追踪的梯度。
(8)outputs = net(inputs) 将输入数据 inputs 输入到模型 net 中进行前向传播，得到模型的输出 outputs。
(9)loss = criterion(outputs, labels) 计算模型输出 outputs 和标签 labels 之间的损失值。
(10)loss.backward() 根据损失值计算参数的梯度。
(11)optimizer.step() 根据梯度更新模型的参数。
(12)running_loss += loss.item() 累计当前训练批次的损失值。
(13)epoch_loss = running_loss / len(trainloader) 计算当前训练周期的平均损失值。
(14)print("Epoch {} Loss: {:.5f}".format(epoch + 1, epoch_loss)) 打印当前训练周期的损失值。
(15)print('Finished training') 打印训练完成的提示。
(16)net.eval() 将模型设置为评估模式。这一步是为了确保模型中的一些特定层（如 Dropout 或 Batch Normalization）在推理过程中起作用，并在训练时处于关闭状态。
(17)correct = 0 初始化一个变量 correct，用于记录分类正确的样本数量。
(18)total = 0 初始化一个变量 total，用于记录总样本数量。
(19)with torch.no_grad(): 在推理过程中，我们不需要计算梯度，因此使用 torch.no_grad() 上下文管理器，禁止梯度计算。
(20)for images, labels in testloader: 这个循环用于遍历测试集数据加载器，每次迭代返回一个批次的测试集输入数据 images 和对应的标签 labels。
(21)images = images.to(device) 将测试集输入数据 images 移动到所选的设备上。
(22)labels = labels.to(device) 将测试集标签数据 labels 移动到所选的设备上。
(23)outputs = net(images) 将测试集输入数据 images 输入到模型 net 中进行前向传播，得到模型的输出 outputs。
(24)_, predicted = torch.max(outputs.data, 1) 通过对输出数据 outputs 进行argmax操作，获得预测结果 predicted，即最大值对应的类别索引。
(25)total += labels.size(0) 累计总样本数量，labels.size(0) 表示当前批次的标签数量。
(26)(predicted == labels).sum().item() 统计预测正确的样本数量。
(27)correct += (predicted == labels).sum().item() 累计分类正确的样本数量。
(28)accuracy = correct / total 计算模型在测试集上的准确率。
(29)print("Validation Accuracy: {:.2%}".format(accuracy)) 打印模型在测试集上的准确率，保留两位小数并以百分比形式显示。
"""
if __name__ == '__main__':
 for epoch in range(num_epochs):
     running_loss = 0.0
     correct_predictions = 0
    # 训练模式
     model.train()
     for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item() * images.size(0)
        _, predicted = torch.max(outputs.data, 1)
        correct_predictions += (predicted == labels).sum().item()
     epoch_loss = running_loss / len(train_loader)
     print("Epoch {} Loss: {:.5f}".format(epoch + 1, epoch_loss))
 print('Finished training')
 # 验证模式
 model.eval()
 test_loss = 0.0
 correct = 0.0
 total = 0
 with torch.no_grad():
        for images, labels in valid_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            test_loss += loss.item() * images.size(0)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
 test_loss /= len(valid_loader)
 accuracy = correct / total
 print("Validation Accuracy: {:.2%}".format(accuracy))
# 保存模型
torch.save(model.state_dict(), 'cat_dog_model.pth')

