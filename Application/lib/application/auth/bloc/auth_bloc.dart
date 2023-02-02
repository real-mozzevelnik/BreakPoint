import 'package:bloc/bloc.dart';
import 'package:brandpoint/application/auth/services/authefication_service.dart';
import 'package:brandpoint/application/storage.dart';
import 'package:brandpoint/models/user.dart';
import 'package:equatable/equatable.dart';

part 'auth_event.dart';
part 'auth_state.dart';

class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final AutheficationService _autheficationService;
  final Storage _storage = Storage();

  AuthBloc(AutheficationService autheficationService)
      : _autheficationService = autheficationService,
        super(AuthInitial()) {
    on<AuthEvent>(
      ((event, emit) async* {
        on<AppLoad>((event, emit) => _appLoad(event, emit));
        on<UserLogIn>((event, emit) => _userLogIn(event, emit));
        on<UserRegistration>((event, emit) => _userRegistration(event, emit));
        on<UserLogOut>((event, emit) => _userLogOut(event, emit));
      }),
    );
  }

  Future _appLoad(AppLoad event, Emitter<AuthState> emit) async {
    emit(AuthLoading());

    try {
      Future.delayed(const Duration(seconds: 4));

      if (await _storage.isHaveToken()) {
        final user = _autheficationService.signInWithToken();
        if (user != null) {
          emit(AuthAutheficated(user: user as User));
        } else {
          emit(AuthNotAutheficated());
        }
      } else {
        emit(AuthNotAutheficated());
      }
    } catch (e) {
      print("error: e");
    }
  }

  Future _userLogIn(UserLogIn event, Emitter<AuthState> emit) async {
    emit(AuthLoading());
    try {
      final user = _autheficationService.signInWithPasswordAndEmail(
          event.email, event.password);
      if (user != null) {
        emit(AuthAutheficated(user: user as User));
      } else {
        emit(AuthNotAutheficated());
      }
    } catch (e) {
      print("error: $e");
    }
  }

  Future _userRegistration(
      UserRegistration event, Emitter<AuthState> emit) async {
    emit(AuthLoading());
    try {
      final user = _autheficationService.registration(
          event.name, event.email, event.password);
      if (user != null) {
        emit(AuthAutheficated(user: user as User));
      } else {
        (AuthNotAutheficated());
      }
    } catch (e) {
      print("error: $e");
    }
  }

  Future _userLogOut(UserLogOut event, Emitter<AuthState> emit) async {
    emit(AuthLoading());
    try {
      _autheficationService.signOut();
      emit(AuthNotAutheficated());
    } catch (e) {
      print("error: $e");
    }
  }
}
