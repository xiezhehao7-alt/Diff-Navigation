FROM osrf/ros:noetic-desktop-focal
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3-pip python3-catkin-tools ros-noetic-mavros ros-noetic-mavros-extras git curl && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
COPY tests_auto/requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt
COPY . /workspace/
CMD ["/bin/bash", "-c", "source /opt/ros/noetic/setup.bash && catkin_make"]
