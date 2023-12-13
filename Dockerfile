# 使用基础镜像
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

# 设置工作目录
WORKDIR /app

# 将本地项目目录下除了.dockerignore中指定的文件外的其他文件复制到容器中
COPY ./requirements ./requirements

# 安装项目所需的 Python 依赖
RUN pip install -r requirements/requirements.txt
RUN pip install -r requirements/requirements-glm6b-lora.txt

# 暴露项目启动端口
EXPOSE 17860

# 运行项目
CMD ["python", "wenda.py", "-t", "glm6b"]