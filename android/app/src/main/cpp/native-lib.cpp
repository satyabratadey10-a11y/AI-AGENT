#include <jni.h>
#include <string>

extern "C" JNIEXPORT jstring JNICALL
Java_com_aiagent_MainActivity_stringFromJNI(JNIEnv* env, jobject /* this */) {
    std::string message = "Hello from C++ (JNI)";
    return env->NewStringUTF(message.c_str());
}
